import logging
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer
from .tokens import account_activation_token
from api.permissions import IsAdminUserOrReadOnly
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt.tokens import RefreshToken

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) +
            str(user.is_active)
        )

account_activation_token = TokenGenerator()

logger = logging.getLogger(__name__)

class TestAuthView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "Authentication successful!"})

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]
    
    @action(detail=True, methods=['post'])
    def ban(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user banned'})
    
    @action(detail=True, methods=['post'])
    def unban(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user unbanned'})

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('acc_active_email.html', {
                    'user': user,
                    'domain': settings.MACHINE_IP,  # Use MACHINE_IP instead of current_site.domain
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = serializer.validated_data.get('email')
                try:
                    send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
                    logger.info(f"Activation email sent to {to_email}")
                except Exception as e:
                    logger.error(f"Failed to send activation email: {str(e)}")
                    return Response({'detail': 'Failed to send activation email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({'detail': 'Please confirm your email address to complete the registration'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ActivateAccount(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'detail': 'Thank you for your email confirmation. Now you can login your account.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)

logger = logging.getLogger(__name__)

class PasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if email:
            associated_user = User.objects.filter(email=email).first()
            if associated_user:
                subject = "Password Reset Requested"
                email_template_name = "password_reset_email.html"
                c = {
                    "email": associated_user.email,
                    'domain': settings.MACHINE_IP,  # Use MACHINE_IP here
                    'site_name': 'Your Site',
                    "uid": urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    "user": associated_user,
                    'token': default_token_generator.make_token(associated_user),
                    'protocol': 'http',  # Change to 'https' if you're using HTTPS
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, email, settings.EMAIL_HOST_USER, [associated_user.email], fail_silently=False)
                    logger.info(f"Password reset email sent to {associated_user.email} for user {associated_user.username} (ID: {associated_user.id})")
                except Exception as e:
                    logger.error(f"Failed to send password reset email: {str(e)}")
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({"success": "Password reset e-mail has been sent."}, status=status.HTTP_200_OK)
        logger.warning(f"Password reset attempted for non-existent email: {email}")
        return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
User = get_user_model()

logger = logging.getLogger(__name__)
User = get_user_model()

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            print(f"Attempting password reset for user: {user.username} (ID: {user.id})")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            print(f"Invalid user ID in password reset attempt: {uidb64}")

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            if new_password:
                print(f"Old password hash: {user.password}")
                user.set_password(new_password)
                user.save()
                print(f"New password hash: {user.password}")
                print(f"Password reset successful for user: {user.username} (ID: {user.id})")
                return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
            else:
                print(f"Password reset attempt without new password for user: {user.username}")
                return Response({'error': 'New password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print(f"Invalid token for password reset: {uidb64}")
            return Response({'error': 'Invalid reset link or token.'}, status=status.HTTP_400_BAD_REQUEST)
        
