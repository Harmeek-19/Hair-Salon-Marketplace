# Hair Salon Management System API


## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Setup and Installation](#setup-and-installation)
5. [Database Configuration](#database-configuration)
6. [Environment Variables](#environment-variables)
7. [Running the Server](#running-the-server)
8. [API Endpoints](#api-endpoints)
9. [Authentication](#authentication)
10. [Models](#models)
11. [Permissions](#permissions)
12. [Search Functionality](#search-functionality)
13. [Geolocation Features](#geolocation-features)
14. [Email Notifications](#email-notifications)
15. [Admin Dashboard](#admin-dashboard)
16. [Favorites System](#favorites-system)
17. [Chain Salon Management](#chain-salon-management)
18. [City Validation](#city-validation)
19. [Stylist Rating](#stylist-rating)
20. [Testing](#testing)
21. [Deployment](#deployment)
22. [Contributing](#contributing)
23. [Troubleshooting](#troubleshooting)
24. [License](#license)

## Project Overview

This project is a comprehensive backend API for a Hair Salon Management System. It provides functionality for managing salons, stylists, appointments, services, and user accounts. The system includes features such as geolocation-based salon search, appointment booking, review system, favorites system, chain salon management, city validation, stylist rating, and an admin dashboard.

## Technology Stack

- Python 3.8+
- Django 5.0.7
- Django REST Framework
- PostgreSQL (for production)
- SQLite (for development)
- JWT for authentication

## Project Structure

```
hairsalon_backend/
│
├── api/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
│
├── authentication/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── booking/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── content/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── coupons/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── dashboard/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── notifications/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── hairsalon_backend/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
└── README.md
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/hairsalon-backend.git
   cd hairsalon-backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   For Windows, if you encounter issues with the GDAL library, use this command:
   ```
   curl -L -o GDAL-312-amd64 https://github.com/cgohlke/geospatial-wheels/releases/download/v2024.2.18/GDAL-3.8.4-cp312-cp312-win_amd64.whl 
   pip install GDAL-3.8.4-cp312-cp312-win_amd64.whl
   ```

4. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

## Database Configuration

The project uses SQLite for development. For production, it's recommended to use PostgreSQL. To configure PostgreSQL:

1. Install PostgreSQL and create a database
2. Update `DATABASES` in `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_db_name',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

## Environment Variables

Create a `.env` file in the project root and add the following:
```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password
```

## Running the Server

```
python manage.py runserver
```

## API Endpoints

### Authentication
- Register: `POST /auth/register/`
- Login: `POST /auth/token/`
- Refresh Token: `POST /auth/token/refresh/`
- Password Reset: `POST /auth/password_reset/`
- Password Reset Confirm: `POST /auth/password_reset_confirm/<uidb64>/<token>/`

### Salons
- List/Create: `GET/POST /api/salons/`
- Retrieve/Update/Delete: `GET/PUT/PATCH/DELETE /api/salons/<id>/`
- Top Rated: `GET /api/salons/top-rated/`
- Nearby: `GET /api/salons/nearby/?lat=<latitude>&lon=<longitude>`
- Analytics: `GET /api/salons/<id>/analytics/`
- Favorite/Unfavorite: `POST /api/salons/<id>/favorite/`

### Stylists
- List/Create: `GET/POST /api/stylists/`
- Retrieve/Update/Delete: `GET/PUT/PATCH/DELETE /api/stylists/<id>/`
- Appointments: `GET /api/stylists/<id>/appointments/`
- Available Slots: `GET /api/stylists/<id>/available_slots/?date=<date>`
- Favorite/Unfavorite: `POST /api/stylists/<id>/favorite/`
- Rate Stylist: `POST /api/stylists/<id>/rate/`

### Services
- List/Create: `GET/POST /api/services/`
- Retrieve/Update/Delete: `GET/PUT/PATCH/DELETE /api/services/<id>/`

### Appointments
- List/Create: `GET/POST /api/appointments/`
- Retrieve/Update/Delete: `GET/PUT/PATCH/DELETE /api/appointments/<id>/`
- Confirm: `POST /api/appointments/<id>/confirm/`
- Cancel: `POST /api/appointments/<id>/cancel/`

### Reviews
- List/Create: `GET/POST /api/reviews/`
- Retrieve/Update/Delete: `GET/PUT/PATCH/DELETE /api/reviews/<id>/`

### Blogs
- List/Create: `GET/POST /api/blogs/`
- Retrieve/Update/Delete: `GET/PUT/PATCH/DELETE /api/blogs/<id>/`

### Coupons
- List/Create: `GET/POST /api/coupons/`
- Retrieve/Update/Delete: `GET/PUT/PATCH/DELETE /api/coupons/<id>/`

### Reports
- Salon Report: `GET /api/reports/salon_report/`
- Stylist Report: `GET /api/reports/stylist_report/`
- Appointment Report: `GET /api/reports/appointment_report/`

### Favorites
- List User's Favorites: `GET /api/favorites/`

## Authentication

The project uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Models

### Salon
- name: CharField
- address: CharField
- city: CharField
- phone: CharField
- email: EmailField
- description: TextField
- is_chain: BooleanField
- chain_name: CharField (optional)
- latitude: FloatField
- longitude: FloatField
- rating: FloatField

### Stylist
- name: CharField
- email: EmailField
- phone: CharField
- specialties: CharField
- salon: ForeignKey to Salon
- years_of_experience: IntegerField
- average_rating: FloatField
- total_ratings: IntegerField

### Service
- name: CharField
- description: TextField
- price: DecimalField
- duration: IntegerField
- salon: ForeignKey to Salon

### Appointment
- customer: ForeignKey to User
- stylist: ForeignKey to Stylist
- salon: ForeignKey to Salon
- services: ManyToManyField to Service
- date: DateField
- start_time: TimeField
- end_time: TimeField
- status: CharField (choices: BOOKED, CONFIRMED, CANCELLED, COMPLETED)
- total_price: DecimalField

### Favorite
- user: ForeignKey to User
- salon: ForeignKey to Salon (optional)
- stylist: ForeignKey to Stylist (optional)
- created_at: DateTimeField

### StylistRating
- user: ForeignKey to User
- stylist: ForeignKey to Stylist
- rating: IntegerField
- comment: TextField
- created_at: DateTimeField

## Permissions

The project uses custom permissions to control access to different parts of the API:
- IsSalonOwner: Allows salon owners to manage their own salons
- IsAdminUser: Allows admin users full access
- IsStylist: Allows stylists to manage their own profiles and appointments
- IsCustomer: Allows customers to book appointments and leave reviews

## Search Functionality

The API provides advanced search capabilities for salons and stylists:
- Search by name, description, services, and city
- Filter by various criteria such as rating, price range, and availability
- Sort results by relevance, rating, or distance (when geolocation is provided)

## Geolocation Features

The API supports geolocation-based queries:
- Find nearby salons based on user's latitude and longitude
- Sort search results by distance from a given location

## Email Notifications

The system sends email notifications for various events:
- Appointment confirmation and reminders
- Password reset requests
- Account activation

## Admin Dashboard

The admin dashboard provides an overview of the system and allows administrators to:
- View and manage salons, stylists, and users
- Generate reports on appointments, revenue, and user activity
- Manage system-wide settings and configurations

## Favorites System

Users can mark salons and stylists as favorites:
- Add/remove salons and stylists from favorites
- View a list of favorite salons and stylists
- Receive notifications about promotions or availability of favorite salons/stylists

## Chain Salon Management

The system supports management of salon chains:
- Create multiple salons with the same name in different cities
- Group analytics and reports for chain salons
- Apply chain-wide promotions and policies

## City Validation

Salon registration is restricted to a predefined list of the top 500 cities in India:
- Prevents registration of salons in non-existent or very small locations
- Ensures data quality and improves search functionality
- Easily expandable to include more cities as needed

## Stylist Rating

Users can rate and review stylists:
- Rate stylists on a scale of 1 to 5
- Leave text reviews for stylists
- View average ratings and read reviews for stylists
- Sort and filter stylists based on their ratings

## Testing

To run the test suite:
```
python manage.py test
```

To test the new features:
1. Test favoriting salons and stylists
2. Attempt to register salons in both valid and invalid cities
3. Try creating chain salons with the same name in different cities
4. Rate stylists and check if the average rating updates correctly

## Deployment

Guidelines for deploying to production:
1. Set DEBUG=False in settings.py
2. Configure a production-ready database (e.g., PostgreSQL)
3. Set up a reverse proxy (e.g., Nginx) and WSGI server (e.g., Gunicorn)
4. Use environment variables for sensitive information
5. Set up SSL/TLS for secure connections
6. Configure static file serving
7. Set up regular backups

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Troubleshooting

- If you encounter database migration issues, try resetting migrations
- For GDAL-related issues on Windows, refer to the installation instructions in the Setup section
- If email notifications are not working, check your email server settings and firewall configurations

## License

This project is licensed under the MIT License.
```

This version should display correctly on GitHub with proper formatting for headers, code blocks, and lists.
