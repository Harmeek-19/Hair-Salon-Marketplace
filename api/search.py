from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Salon, Stylist, Service
from .serializers import SalonSearchSerializer, StylistSerializer, ServiceSerializer
import logging

logger = logging.getLogger(__name__)

class GlobalSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        search_type = request.query_params.get('type', 'all')

        logger.info(f"Search query: {query}, Type: {search_type}")

        results = {}

        if search_type in ['all', 'salon']:
            salons = Salon.objects.filter(
                Q(name__icontains=query) | 
                Q(address__icontains=query) | 
                Q(city__icontains=query) |
                Q(description__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            )
            logger.info(f"Found {salons.count()} salons")
            logger.info(f"Query: {salons.query}")
            for salon in salons:
                logger.info(f"Salon: {salon.name}, Address: {salon.address}")
            results['salons'] = SalonSearchSerializer(salons, many=True).data

        if search_type in ['all', 'stylist']:
            stylists = Stylist.objects.filter(
                Q(name__icontains=query) | 
                Q(specialties__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            )
            results['stylists'] = StylistSerializer(stylists, many=True).data

        if search_type in ['all', 'service']:
            services = Service.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
            results['services'] = ServiceSerializer(services, many=True).data

        logger.info(f"Search results: {results}")
        return Response(results)