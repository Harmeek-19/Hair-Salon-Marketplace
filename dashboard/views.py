from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from api.models import Salon, Service
from authentication.models import User
from booking.models import Appointment as BookingAppointment
from django.db.models import Count, Sum
from django.utils import timezone
from django.shortcuts import render
from .models import AdminDashboardSetting
from django.db.models import Count, Sum

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_staff:
            return self.admin_dashboard(request)
        elif user.role == 'salon_owner':
            return self.salon_owner_dashboard(request)
        elif user.role == 'stylist':
            return self.stylist_dashboard(request)
        else:
            return self.customer_dashboard(request)

    def admin_dashboard(self, request):
        today = timezone.now().date()
        last_30_days = today - timezone.timedelta(days=30)

        data = {
            "user_stats": self.get_user_stats(),
            "salon_stats": self.get_salon_stats(),
            "appointment_stats": self.get_appointment_stats(last_30_days),
            "revenue_stats": self.get_revenue_stats(last_30_days),
            "recent_activities": self.get_recent_activities(),
        }
        return Response(data)

    def get_user_stats(self):
        return {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "new_users_last_30_days": User.objects.filter(date_joined__gte=timezone.now() - timezone.timedelta(days=30)).count(),
            "user_roles": User.objects.values('role').annotate(count=Count('id')),
        }

    def get_salon_stats(self):
        return {
            "total_salons": Salon.objects.count(),
            "active_salons": Salon.objects.filter(is_active=True).count(),
            "top_rated_salons": Salon.objects.order_by('-rating')[:5].values('name', 'rating'),
            "salons_by_city": Salon.objects.values('city').annotate(count=Count('id')),
        }

    def get_appointment_stats(self, last_30_days):
        return {
            "total_appointments": BookingAppointment.objects.count(),
            "appointments_last_30_days": BookingAppointment.objects.filter(date__gte=last_30_days).count(),
            "appointments_by_status": BookingAppointment.objects.values('status').annotate(count=Count('id')),
            "popular_services": Service.objects.annotate(appointment_count=Count('appointment')).order_by('-appointment_count')[:5].values('name', 'appointment_count'),
        }

    def get_revenue_stats(self, last_30_days):
        total_revenue = BookingAppointment.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        revenue_last_30_days = BookingAppointment.objects.filter(status='completed', date__gte=last_30_days).aggregate(Sum('total_price'))['total_price__sum'] or 0
        return {
            "total_revenue": total_revenue,
            "revenue_last_30_days": revenue_last_30_days,
            "average_appointment_value": total_revenue / BookingAppointment.objects.filter(status='completed').count() if BookingAppointment.objects.filter(status='completed').exists() else 0,
        }

    def get_recent_activities(self):
        recent_appointments = BookingAppointment.objects.order_by('-created_at')[:10].values('id', 'customer__username', 'salon__name', 'date', 'status')
        recent_users = User.objects.order_by('-date_joined')[:10].values('id', 'username', 'email', 'date_joined')
        recent_salons = Salon.objects.order_by('-id')[:10].values('id', 'name', 'city', 'rating')
        return {
            "recent_appointments": list(recent_appointments),
            "recent_users": list(recent_users),
            "recent_salons": list(recent_salons),
        }

    def customer_dashboard(self, request):
        user = request.user
        upcoming_appointments = BookingAppointment.objects.filter(customer=user, date__gte=timezone.now().date()).order_by('date')[:5]
        
        data = {
            "username": user.username,
            "upcoming_appointments": upcoming_appointments.values('salon__name', 'stylist__name', 'date', 'start_time'),
            "favorite_salons": user.favorite_salons.all()[:5].values('name', 'city'),
            "recent_reviews": user.reviews.order_by('-created_at')[:5].values('salon__name', 'rating', 'comment'),
        }
        return Response(data)
    
    def stylist_dashboard(self, request):
        stylist = request.user.stylist_profile
        if not stylist:
            return Response({"error": "No stylist profile found for this user"}, status=404)

        today = timezone.now().date()
        appointments = BookingAppointment.objects.filter(stylist=stylist, date=today)

        data = {
            "stylist_name": stylist.name,
            "today_appointments": appointments.count(),
            "upcoming_appointments": BookingAppointment.objects.filter(stylist=stylist, date__gt=today).count(),
            "recent_reviews": stylist.reviews.order_by('-created_at')[:5].values('rating', 'comment'),
            "popular_services": Service.objects.filter(appointment__stylist=stylist).annotate(count=Count('appointment')).order_by('-count')[:5].values('name', 'count'),
        }
        return Response(data)
    
    def salon_owner_dashboard(self, request):
        salon = Salon.objects.filter(owner=request.user).first()
        if not salon:
            return Response({"error": "No salon found for this user"}, status=404)

        today = timezone.now().date()
        appointments = BookingAppointment.objects.filter(salon=salon, date=today)
        
        data = {
            "salon_name": salon.name,
            "today_appointments": appointments.count(),
            "total_stylists": salon.stylists.count(),
            "recent_reviews": salon.reviews.order_by('-created_at')[:5].values('rating', 'comment'),
            "popular_services": Service.objects.filter(appointment__salon=salon).annotate(count=Count('appointment')).order_by('-count')[:5].values('name', 'count'),
            "total_revenue": BookingAppointment.objects.filter(salon=salon, status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0,
        }
        return Response(data)

class QuickActionsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        action = request.data.get('action')
        if action == 'disable_user':
            return self.disable_user(request.data.get('user_id'))
        elif action == 'feature_salon':
            return self.feature_salon(request.data.get('salon_id'))
        # Add more quick actions as needed
        return Response({"error": "Invalid action"}, status=404)

    def disable_user(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            return Response({"message": f"User {user.username} has been disabled"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

    def feature_salon(self, salon_id):
        try:
            salon = Salon.objects.get(id=salon_id)
            salon.is_featured = True
            salon.save()
            return Response({"message": f"Salon {salon.name} has been featured"})
        except Salon.DoesNotExist:
            return Response({"error": "Salon not found"}, status=404)