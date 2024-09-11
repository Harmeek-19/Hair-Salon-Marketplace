from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (BlogPostListCreateView, BlogPostDetailView, 
                    StaticPageListCreateView, StaticPageDetailView, 
                    FAQViewSet, ContactFormView)

router = DefaultRouter()
router.register(r'faqs', FAQViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('blogs/', BlogPostListCreateView.as_view(), name='blog-list-create'),
    path('blogs/<int:pk>/', BlogPostDetailView.as_view(), name='blog-detail'),
    path('pages/', StaticPageListCreateView.as_view(), name='static-page-list-create'),
    path('pages/<int:pk>/', StaticPageDetailView.as_view(), name='static-page-detail'),
    path('contact/', ContactFormView.as_view(), name='contact-form'),
]