from rest_framework import generics, permissions, viewsets
from .models import Blog, StaticPage, FAQ
from .serializers import BlogPostSerializer, StaticPageSerializer, FAQSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework import viewsets, permissions
from .models import FAQ
from .serializers import FAQSerializer


class BlogPostListCreateView(generics.ListCreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class StaticPageListCreateView(generics.ListCreateAPIView):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class StaticPageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



class ContactFormView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        message = request.data.get('message')
        
        # Send email
        send_mail(
            f'Contact Form Submission from {name}',
            message,
            email,
            ['your-email@example.com'],
            fail_silently=False,
        )
        
        return Response({"message": "Your message has been sent successfully."})
    

class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminUserOrReadOnly]