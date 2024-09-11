from django.test import TransactionTestCase
from django.urls import reverse
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token

User = get_user_model()

class AuthenticationTests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-registration')
        self.login_url = reverse('token_obtain_pair')
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'role': 'customer'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
        self.assertFalse(User.objects.get().is_active)  # User should be inactive until email verification

    def test_user_registration(self):
        initial_user_count = User.objects.count()
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        self.assertEqual(User.objects.last().username, 'testuser')
        self.assertFalse(User.objects.last().is_active)

    def test_email_verification_sent(self):
        self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Activate your account.')

    def test_email_verification(self):
        self.client.post(self.register_url, self.user_data, format='json')
        user = User.objects.get(username='testuser')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_login_unverified_user(self):
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_verified_user(self):
        self.client.post(self.register_url, self.user_data, format='json')
        user = User.objects.get(username='testuser')
        user.is_active = True
        user.save()
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_password_reset_request(self):
        user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass123')
        url = reverse('password_reset')
        response = self.client.post(url, {'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password Reset Requested')

    # Add more tests as needed...