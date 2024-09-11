from django.db.models import Count, Avg, Q
from .models import Salon, Stylist
from booking.models import Appointment

def get_salon_report():
    return Salon.objects.annotate(
        stylist_count=Count('stylists'),
        avg_rating=Avg('rating')
    ).values('id', 'name', 'stylist_count', 'avg_rating')

def get_stylist_report():
    return Stylist.objects.annotate(
        total_appointments=Count('appointments'),
        average_rating=Avg('appointments__review__rating'),
        completed_appointments=Count('appointments', filter=Q(appointments__status='COMPLETED'))
    ).values(
        'id', 'name', 'total_appointments', 'average_rating', 'completed_appointments'
    )

def get_appointment_report():
    return Appointment.objects.values('status').annotate(count=Count('id'))