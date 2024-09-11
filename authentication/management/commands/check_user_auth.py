from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

class Command(BaseCommand):
    help = 'Check user authentication and password status'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"User found: {user.username} (ID: {user.id})")
            self.stdout.write(f"Email: {user.email}")
            self.stdout.write(f"Is active: {user.is_active}")
            
            if check_password(password, user.password):
                self.stdout.write(self.style.SUCCESS("Password is correct"))
            else:
                self.stdout.write(self.style.ERROR("Password is incorrect"))
                self.stdout.write(f"Stored password hash: {user.password}")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with username '{username}' does not exist"))