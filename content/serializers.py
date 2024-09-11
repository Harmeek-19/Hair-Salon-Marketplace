from rest_framework import serializers
from .models import Blog, StaticPage, FAQ

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'