import django_filters
from .models import Salon, Stylist
from booking.models import Appointment
from django_filters import rest_framework as filters

class SalonFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name="rating", lookup_expr='lte')

    class Meta:
        model = Salon
        fields = ['name', 'address', 'min_rating', 'max_rating']

class StylistFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    min_experience = django_filters.NumberFilter(field_name="years_of_experience", lookup_expr='gte')

    class Meta:
        model = Stylist
        fields = ['name', 'specialties', 'salon', 'min_experience']

class AppointmentFilter(django_filters.FilterSet):
    min_date = django_filters.DateFilter(field_name="date", lookup_expr='gte')
    max_date = django_filters.DateFilter(field_name="date", lookup_expr='lte')
    
    class Meta:
        model = Appointment
        fields = ['stylist', 'service', 'min_date', 'max_date', 'status']
    
    service = filters.CharFilter(field_name='services__name', lookup_expr='icontains')
    class Meta:
        model = Appointment
        fields = ['stylist', 'date', 'status']