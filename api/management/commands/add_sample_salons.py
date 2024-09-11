from django.core.management.base import BaseCommand
from api.models import Salon, Stylist

class Command(BaseCommand):
    help = 'Adds sample salon and stylist data to the database'

    def handle(self, *args, **kwargs):
        salons_data = [
            {
                "name": "Glamour Salon",
                "address": "123 Main St",
                "city": "Mumbai",
                "phone": "+919876543210",
                "email": "glamour@example.com",
                "description": "A high-end salon in the heart of Mumbai",
                "is_chain": False,
                "latitude": 19.0760,
                "longitude": 72.8777
            },
            {
                "name": "StyleChain",
                "address": "456 Oak St",
                "city": "Delhi",
                "phone": "+919876543211",
                "email": "stylechain.delhi@example.com",
                "description": "Part of the StyleChain franchise in Delhi",
                "is_chain": True,
                "chain_name": "StyleChain",
                "latitude": 28.6139,
                "longitude": 77.2090
            },
            {
                "name": "StyleChain",
                "address": "789 Elm St",
                "city": "Mumbai",
                "phone": "+919876543212",
                "email": "stylechain.mumbai@example.com",
                "description": "Part of the StyleChain franchise in Mumbai",
                "is_chain": True,
                "chain_name": "StyleChain",
                "latitude": 19.0760,
                "longitude": 72.8777
            },
            {
                "name": "Curl Up & Dye",
                "address": "101 Banyan Ave",
                "city": "Bangalore",
                "phone": "+919876543213",
                "email": "curlup@example.com",
                "description": "Quirky salon with a sense of humor",
                "is_chain": False,
                "latitude": 12.9716,
                "longitude": 77.5946
            },
        ]

        stylists_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+919876543214",
                "specialties": "Haircut, Coloring",
                "years_of_experience": 5
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+919876543215",
                "specialties": "Styling, Perming",
                "years_of_experience": 8
            },
            {
                "name": "Mike Johnson",
                "email": "mike@example.com",
                "phone": "+919876543216",
                "specialties": "Beard Trimming, Facials",
                "years_of_experience": 3
            },
        ]

        for salon_data in salons_data:
            salon, created = Salon.objects.get_or_create(
                name=salon_data['name'],
                city=salon_data['city'],
                defaults=salon_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully added salon "{salon.name}" in {salon.city}'))
            else:
                self.stdout.write(self.style.WARNING(f'Salon "{salon.name}" in {salon.city} already exists'))

        # Assign stylists to salons
        salons = list(Salon.objects.all())
        for i, stylist_data in enumerate(stylists_data):
            salon = salons[i % len(salons)]  # Distribute stylists across salons
            stylist, created = Stylist.objects.get_or_create(
                name=stylist_data['name'],
                email=stylist_data['email'],
                defaults={**stylist_data, 'salon': salon}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully added stylist "{stylist.name}" to "{salon.name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Stylist "{stylist.name}" already exists'))