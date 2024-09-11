from rest_framework import serializers
from api.models import Favorite, Salon, Stylist, Service, Promotion, StylistRating
from booking.models import Appointment
from content.models import Review, Blog
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .views import haversine_distance
from rest_framework import serializers
from api.models import Salon, Stylist, Service, Promotion
from booking.models import Appointment
from content.models import Review, Blog

class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = ['id', 'name', 'address', 'city', 'phone', 'email', 'latitude', 'longitude', 'description', 'rating']

    def get_distance(self, obj):
        return getattr(obj, 'distance', None)
    
    def get_is_favorite(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and Favorite.objects.filter(user=user, salon=obj).exists()

class SalonSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = ['id', 'name', 'address', 'city', 'phone', 'email', 'latitude', 'longitude', 'description', 'rating']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['distance'] = getattr(instance, 'distance', None)
        return representation
    
class StylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stylist
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        if user and Stylist.objects.exclude(pk=self.instance.pk if self.instance else None).filter(user=user).exists():
            raise serializers.ValidationError("This user is already associated with another stylist profile.")
        return data

    def get_is_favorite(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and Favorite.objects.filter(user=user, stylist=obj).exists()
    
    
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all(), required=False)

    class Meta:
        model = Appointment
        fields = ['id', 'customer', 'stylist', 'salon', 'services', 'date', 'start_time', 'end_time', 'status', 'total_price', 'notes']
        read_only_fields = ['status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['services'] = [{'id': service.id, 'name': service.name} for service in instance.services.all()]
        return representation
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

class StylistRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StylistRating
        fields = '__all__'