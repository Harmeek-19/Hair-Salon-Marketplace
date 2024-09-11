from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    CUSTOMER = 'customer'
    SALON_OWNER = 'salon_owner'
    STYLIST = 'stylist'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'
    
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (SALON_OWNER, 'Salon Owner'),
        (STYLIST, 'Stylist'),
        (ADMIN, 'Admin'),
        (SUPER_ADMIN, 'Super Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    phone_number = models.CharField(max_length=15, blank=True)
    country_code = models.CharField(max_length=5, blank=True)

class SalonClaim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    salon = models.ForeignKey('api.Salon', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

class StylistClaim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    salon = models.ForeignKey('api.Salon', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)