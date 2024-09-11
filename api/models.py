from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from authentication.models import User

class Salon(models.Model):
    salon_id = models.CharField(max_length=50, unique=True, blank=True)
    small_area_name = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=15, 
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    email = models.EmailField(null=True, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    services = models.TextField(blank=True)
    salon_photos = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    building_name = models.CharField(max_length=100, blank=True)
    post_code = models.CharField(max_length=20, blank=True)
    area_name = models.CharField(max_length=100, blank=True)
    is_chain = models.BooleanField(default=False)
    chain_name = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, blank=True)
    opening_hour = models.TimeField(null=True, blank=True)
    closing_hour = models.TimeField(null=True, blank=True)
    menu_link = models.URLField(blank=True)
    menu_photos = models.TextField(blank=True)
    menu_text = models.TextField(blank=True)
    rating = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    owner = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_salons'
    )

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['city']),
            models.Index(fields=['rating']),
        ]
        constraints = [
                models.UniqueConstraint(
                    fields=['name', 'city'],
                    condition=models.Q(is_chain=False),
                    name='unique_salon_name_per_city'
                )
            ]
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        if not self.salon_id:
            self.salon_id = self.generate_unique_salon_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_salon_id():
        return get_random_string(length=10)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes")
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='service_items')
    
    def __str__(self):
        return self.name



class Stylist(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(
        max_length=15, 
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        blank=True
    )
    specialties = models.CharField(max_length=200, blank=True)
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)
    user = models.OneToOneField(
        'authentication.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='stylist_profile'
    )
    workplace = models.ForeignKey(Salon, on_delete=models.SET_NULL, null=True, related_name='workplace_stylists')
    years_of_experience = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='stylists')
    photos = models.TextField(blank=True)

    def clean(self):
        if self.years_of_experience < 0:
            raise ValidationError('Years of experience cannot be negative')
        if self.user and Stylist.objects.exclude(pk=self.pk).filter(user=self.user).exists():
            raise ValidationError("This user is already associated with another stylist profile.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Promotion(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    discount_percentage = models.IntegerField()
    valid_until = models.DateTimeField()

    def __str__(self):
        return self.title

# Add this new model
class StylistRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stylist = models.ForeignKey(Stylist, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'stylist')
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='favorited_by', null=True, blank=True)
    stylist = models.ForeignKey(Stylist, on_delete=models.CASCADE, related_name='favorited_by', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'salon', 'stylist')
        constraints = [
            models.CheckConstraint(
                check=models.Q(salon__isnull=False) | models.Q(stylist__isnull=False),
                name='favorite_salon_or_stylist'
            )
        ]