from django.contrib import admin
from .models import Salon, Stylist, Service
from booking.models import Appointment

class StylistInline(admin.TabularInline):
    model = Stylist
    fk_name = 'salon'  # Specify which ForeignKey to use
    extra = 1

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    inlines = [StylistInline]
    list_display = ('name', 'city', 'phone', 'email')
    search_fields = ('name', 'city')

@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'workplace', 'specialties', 'years_of_experience')
    list_filter = ('salon', 'workplace')
    search_fields = ('name', 'salon__name', 'workplace__name')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')
    search_fields = ('name',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'stylist', 'salon', 'get_services', 'date', 'start_time', 'status')
    
    def get_services(self, obj):
        return ", ".join([service.name for service in obj.services.all()])
    get_services.short_description = 'Services'