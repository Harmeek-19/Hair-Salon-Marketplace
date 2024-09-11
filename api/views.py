from audioop import avg
from math import radians, sin, cos, sqrt, atan2

from api.utils import is_valid_city

def haversine_distance(lat1, lon1, lat2, lon2):
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None
    
    R = 6371  # Earth radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance

    return distance
from django.db.models import Count, Sum, Avg
from rest_framework import viewsets, serializers, status, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action, api_view, permission_classes
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import Favorite, Salon, Stylist, Service, Promotion, StylistRating
from booking.models import Appointment
from content.models import Review, Blog
from .serializers import (FavoriteSerializer, SalonSerializer, StylistRatingSerializer, StylistSerializer, ServiceSerializer, AppointmentSerializer, ReviewSerializer, BlogSerializer, PromotionSerializer)
from authentication.models import User
from .permissions import IsSalonOwnerOrReadOnly, IsAdminUserOrReadOnly, IsStylist, IsSalonOwner
from .reports import get_salon_report, get_stylist_report, get_appointment_report
from rest_framework.permissions import BasePermission
from .serializers import (
    SalonSerializer, StylistSerializer, ServiceSerializer, 
    AppointmentSerializer, ReviewSerializer, BlogSerializer, 
    PromotionSerializer)
from django.db import IntegrityError
from rest_framework import status
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from booking.models import Appointment
from .models import Salon, Service
from .serializers import AppointmentSerializer, SalonSerializer
from django.http import JsonResponse


class CanClaimSalon(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'salon_owner'

class TestAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authentication successful!"})

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('id')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'price', 'salon']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'duration']
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

class SalonViewSet(viewsets.ModelViewSet):
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'address', 'description']
    ordering_fields = ['name', 'id', 'rating']

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        
        if lat is None or lon is None:
            return Response({"error": "Latitude and longitude are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return Response({"error": "Invalid latitude or longitude."}, status=status.HTTP_400_BAD_REQUEST)
        
        salons = Salon.objects.all()
        
        salons_with_distance = []
        for salon in salons:
            if salon.latitude is not None and salon.longitude is not None:
                distance = haversine_distance(lat, lon, salon.latitude, salon.longitude)
                if distance is not None:
                    salon.distance = distance
                    salons_with_distance.append((salon, distance))
        
        salons_with_distance.sort(key=lambda x: x[1])
        nearby_salons = [salon for salon, _ in salons_with_distance[:6]]  # Get top 6 nearest salons
        
        serializer = self.get_serializer(nearby_salons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stylists(self, request, pk=None):
        salon = self.get_object()
        stylists = salon.stylists.all()
        serializer = StylistSerializer(stylists, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        salon = self.get_object()
        appointments = Appointment.objects.filter(salon=salon)
        
        # Get popular services
        popular_services = Service.objects.filter(appointments__in=appointments).annotate(
            count=Count('appointments')
        ).order_by('-count')[:5]
        
        # Calculate revenue
        revenue = appointments.filter(status='COMPLETED').aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        data = {
            'total_appointments': appointments.count(),
            'completed_appointments': appointments.filter(status='COMPLETED').count(),
            'popular_services': [{'name': s.name, 'count': s.count} for s in popular_services],
            'total_revenue': revenue,
        }
        return Response(data)
    
    @action(detail=True, methods=['post'], permission_classes=[CanClaimSalon])
    def claim(self, request, pk=None):
        print(f"Claim attempt by user: {request.user.username}")
        salon = self.get_object()
        if salon.owner:
            print(f"Salon {salon.id} is already owned by {salon.owner.username}")
            return Response({"detail": "This salon is already claimed."}, status=status.HTTP_400_BAD_REQUEST)
        
        salon.owner = request.user
        salon.save()
        print(f"Salon {salon.id} claimed by {request.user.username}")
        return Response({"detail": "Salon claim request submitted for review."})

    @action(detail=False, methods=['get'], url_path='top-rated', url_name='top_rated')
    def top_rated(self, request):
        print("Top rated method called")  # Add this line
        top_salons = self.get_queryset().order_by('-rating')[:4]
        print(f"Top salons: {top_salons}")  # Add this line
        serializer = self.get_serializer(top_salons, many=True)
        return Response(serializer.data)
    
    def test_top_rated(request):
        return JsonResponse({"message": "Test top rated view"})
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        return self.top_rated(request)
    
    def create(self, request, *args, **kwargs):
        city = request.data.get('city')
        if not is_valid_city(city):
            return Response({"error": "Invalid city. Salon can only be registered in one of the top 500 cities in India."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        salon = self.get_object()
        user = request.user
        favorite, created = Favorite.objects.get_or_create(user=user, salon=salon)
        if created:
            return Response({"status": "favorited"})
        favorite.delete()
        return Response({"status": "unfavorited"})

class StylistViewSet(viewsets.ModelViewSet):
    queryset = Stylist.objects.all()
    serializer_class = StylistSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'specialties', 'salon', 'workplace']
    search_fields = ['name', 'specialties', 'email']
    ordering_fields = ['name', 'years_of_experience']

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        stylist = self.get_object()
        appointments = Appointment.objects.filter(stylist=stylist)
        print(f"Stylist: {stylist.name}, Appointments count: {appointments.count()}")
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def available_slots(self, request, pk=None):
        stylist = self.get_object()
        date = request.query_params.get('date', datetime.now().date())
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        
        start_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=9)
        end_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=17)
        
        # Change this line to use 'start_time' instead of 'time'
        booked_slots = Appointment.objects.filter(stylist=stylist, date=date).values_list('start_time', flat=True)
        
        available_slots = []
        current_slot = start_time
        while current_slot < end_time:
            if current_slot.time() not in booked_slots:
                available_slots.append(current_slot.strftime('%H:%M'))
            current_slot += timedelta(minutes=30)
        
        return Response(available_slots)

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        stylist = self.get_object()
        if stylist.user:
            return Response({"detail": "This stylist profile is already claimed."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            stylist.user = request.user
            stylist.save()
            return Response({"detail": "Stylist profile claim request submitted for review."})
        except IntegrityError:
            return Response({"detail": "You have already claimed a stylist profile."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        stylist = self.get_object()
        user = request.user
        favorite, created = Favorite.objects.get_or_create(
            user=user,
            stylist=stylist,
            defaults={'salon': stylist.salon}  # Add this line
        )
        if created:
            return Response({"status": "favorited"})
        favorite.delete()
        return Response({"status": "unfavorited"})

    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        stylist = self.get_object()
        user = request.user
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if not rating:
            return Response({"error": "Rating is required"}, status=status.HTTP_400_BAD_REQUEST)

        stylist_rating, created = StylistRating.objects.update_or_create(
            user=user, stylist=stylist,
            defaults={'rating': rating, 'comment': comment}
        )

        # Update stylist's average rating
        stylist.total_ratings = StylistRating.objects.filter(stylist=stylist).count()
        stylist.average_rating = StylistRating.objects.filter(stylist=stylist).aggregate(Avg('rating'))['rating__avg']
        stylist.save()

        return Response(StylistRatingSerializer(stylist_rating).data)

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        try:
            appointment = self.get_object()
            appointment.status = 'CANCELLED'
            appointment.save()
            
            serializer = self.get_serializer(appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        try:
            appointment = self.get_object()
            appointment.status = 'CONFIRMED'
            appointment.save()
            return Response({'status': 'appointment confirmed'}, status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_create(self, serializer):
        stylist = serializer.validated_data['stylist']
        date = serializer.validated_data['date']
        start_time = serializer.validated_data['start_time']
        
        if Appointment.objects.filter(stylist=stylist, date=date, start_time=start_time).exists():
            raise serializers.ValidationError("This time slot is already booked.")
        
        appointment = serializer.save()
        
        # Add services to the appointment
        services = serializer.validated_data.get('services', [])
        appointment.services.set(services)
        
        subject = 'New Appointment Booked'
        message = f'You have a new appointment on {appointment.date} at {appointment.start_time}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [appointment.stylist.email, appointment.customer.email]
        send_mail(subject, message, from_email, recipient_list)

class AppointmentFilter(filters.FilterSet):
    service = filters.ModelMultipleChoiceFilter(
        field_name='services__name',
        to_field_name='name',
        queryset=Service.objects.all()
    )

    class Meta:
        model = Appointment
        fields = ['stylist', 'date', 'status', 'service']

class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]

    @action(detail=False, methods=['get'])
    def salon_report(self, request):
        return Response(get_salon_report())

    @action(detail=False, methods=['get'])
    def stylist_report(self, request):
        return Response(get_stylist_report())

    @action(detail=False, methods=['get'])
    def appointment_report(self, request):
        return Response(get_appointment_report())

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def delete_review(self, request, pk=None):
        if request.user.is_staff or request.user.is_superuser:
            review = self.get_object()
            review.delete()
            return Response({"detail": "Review deleted successfully."})
        return Response({"detail": "You don't have permission to delete this review."}, status=status.HTTP_403_FORBIDDEN)

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]


class NotificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        message = request.data.get('message')
        users = User.objects.all()
        
        for user in users:
            # Implement your preferred method to send notifications here
            pass
        
        return Response({"detail": "Notifications sent successfully."})

class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_salon_with_stylists(request):
    salon_data = request.data.get('salon')
    stylists_data = request.data.get('stylists', [])
    
    # Create salon
    salon_serializer = SalonSerializer(data=salon_data)
    if salon_serializer.is_valid():
        salon = salon_serializer.save(owner=request.user)
        
        # Create stylists
        created_stylists = []
        for stylist_data in stylists_data:
            stylist_data['salon'] = salon.id
            stylist_serializer = StylistSerializer(data=stylist_data)
            if stylist_serializer.is_valid():
                stylist = stylist_serializer.save()
                created_stylists.append(stylist_serializer.data)
            else:
                return Response(stylist_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'salon': salon_serializer.data,
            'stylists': created_stylists
        }, status=status.HTTP_201_CREATED)
    
    return Response(salon_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsSalonOwner])
def delete_salon(request, salon_id):
    try:
        salon = Salon.objects.get(id=salon_id)
        salon.delete()
        return Response({"message": "Salon and associated stylists deleted successfully"}, status=status.HTTP_200_OK)
    except Salon.DoesNotExist:
        return Response({"error": "Salon not found"}, status=status.HTTP_404_NOT_FOUND)    

class SuperAdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        total_salons = Salon.objects.count()
        total_appointments = Appointment.objects.count()
        
        return Response({
            "total_users": total_users,
            "total_salons": total_salons,
            "total_appointments": total_appointments,
        })

class FavoriteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
