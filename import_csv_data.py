import os
import django
import pandas as pd
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.dateparse import parse_time
import datetime
import sys

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hairsalon_backend.settings")
django.setup()

from api.models import Salon, Stylist
from content.models import Review

def parse_menu(menu_str):
    return menu_str.replace(',', ', ') if isinstance(menu_str, str) else ''

def clean_time(time_str):
    if pd.isna(time_str):
        return None
    time_str = str(time_str).strip()
    if ':' not in time_str:
        time_str += ':00'
    return time_str

def parse_time_safely(time_str):
    if pd.isna(time_str):
        return None
    time_str = clean_time(time_str)
    try:
        # Try parsing as HH:MM
        return datetime.datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        try:
            # Try parsing as HH:MM:SS
            return datetime.datetime.strptime(time_str, '%H:%M:%S').time()
        except ValueError:
            print(f"Invalid time format: {time_str}")
            return None

def import_csv_data(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path, encoding='utf-8')
    print(f"Total rows in CSV: {len(df)}")
    
    # Print column names
    print("CSV Columns:")
    print(df.columns)
    
    # Clean and prepare the data
    df['latitude'] = pd.to_numeric(df['Latitude(M)'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating 1-5(M)'], errors='coerce')
    
    salons_created = 0
    stylists_created = 0
    reviews_created = 0
    
    for index, row in df.iterrows():
        try:
            with transaction.atomic():
                salon, created = Salon.objects.update_or_create(
                    salon_id=row['Salon ID'],
                    defaults={
                        'small_area_name': row['Small Areaname'],
                        'name': row['Salon name(M)'],
                        'phone': row['10 digit phone number without the code(M)'],
                        'email': row['Email'],
                        'website': row['Website(M)'],
                        'services': row['Comma separated services( no spaces) (M)'],
                        'salon_photos': row['salon photos'],
                        'address': row['Address ( M)'],
                        'latitude': row['latitude'],
                        'longitude': row['longitude'],
                        'building_name': row['Building name'],
                        'post_code': row['Post code'],
                        'area_name': row['Area name'],
                        'city': row['City'],
                        'state': row['State'],
                        'country': row['Country'],
                        'category': row['Category'],
                        'opening_hour': parse_time_safely(row['Opening hour']),
                        'closing_hour': parse_time_safely(row['closing hour\n24 hours format\n14:30 (M)']),
                        'menu_link': row['menu link'],
                        'menu_photos': row['Menu photos google drive link'],
                        'menu_text': parse_menu(row['Menu in text format (Item_name:Price)\n(eg haircut:140,dying:300,colouring:600)']),
                        'rating': row['rating']
                    }
                )
                if created:
                    salons_created += 1

                # Create Stylists
                for i in range(1, 4):
                    stylist_name = row.get(f'Stylist{i} name')
                    if pd.notna(stylist_name):
                        _, stylist_created = Stylist.objects.update_or_create(
                            name=stylist_name,
                            salon=salon,
                            defaults={
                                'specialties': row.get(f'Stylist speciality', ''),
                                'photos': row.get(f'Stylist Photos drive link', '')
                            }
                        )
                        if stylist_created:
                            stylists_created += 1

                # Create Salon Reviews
                for i in range(1, 9):
                    review_key = f'Reviews{i} Salon' if i > 1 else 'Salon Reviews1(M)'
                    review_text = row.get(review_key)
                    if pd.notna(review_text):
                        Review.objects.create(salon=salon, text=review_text)
                        reviews_created += 1

            print(f"Successfully imported data for salon: {salon.name}")

        except ValidationError as e:
            print(f"Validation error for salon {row['Salon name(M)']} at row {index}: {str(e)}")
            print(f"Problematic data: {row}")
        except Exception as e:
            print(f"Error importing data for salon {row['Salon name(M)']} at row {index}: {str(e)}")
            print(f"Problematic data: {row}")

    print(f"Import completed. Created {salons_created} salons, {stylists_created} stylists, and {reviews_created} reviews.")

if __name__ == "__main__":
    csv_file_path = "/home/harmeek/Devlop/Salondata .csv"
    
    if not os.path.exists(csv_file_path):
        print(f"Error: The file {csv_file_path} does not exist.")
        sys.exit(1)
    
    import_csv_data(csv_file_path)

    # Print final counts
    print(f"Final counts in database:")
    print(f"Salons: {Salon.objects.count()}")
    print(f"Stylists: {Stylist.objects.count()}")
    print(f"Reviews: {Review.objects.count()}")