from django.core.management.base import BaseCommand
from api.models import Salon

class Command(BaseCommand):
    help = 'Manage salons in the database'

    def handle(self, *args, **options):
        # Count existing salons
        salon_count = Salon.objects.count()
        self.stdout.write(f"Current number of salons: {salon_count}")

        # List existing salons
        self.stdout.write("Existing salons:")
        for salon in Salon.objects.all():
            self.stdout.write(f"ID: {salon.id}, Name: {salon.name}, Address: {salon.address}")

        # Add new salons if there are fewer than 5
        if salon_count < 5:
            new_salons = [
                Salon(name="Style Hub", address="789 Oak St", city="New York", phone="555-0123"),
                Salon(name="Beauty Corner", address="456 Pine Ave", city="Los Angeles", phone="555-4567"),
                Salon(name="Hair Masters", address="123 Elm Rd", city="Chicago", phone="555-8901"),
            ]
            Salon.objects.bulk_create(new_salons)
            self.stdout.write(self.style.SUCCESS(f"Added {len(new_salons)} new salons"))

        # Count salons again
        new_salon_count = Salon.objects.count()
        self.stdout.write(f"New number of salons: {new_salon_count}")