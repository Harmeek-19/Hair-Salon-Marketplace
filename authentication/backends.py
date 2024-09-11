from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
            if user.check_password(password):
                logger.info(f"Authentication successful for user: {username}")
                return user
            else:
                logger.warning(f"Authentication failed for user: {username} - Invalid password")
        except UserModel.DoesNotExist:
            logger.warning(f"Authentication failed - User does not exist: {username}")
        return None