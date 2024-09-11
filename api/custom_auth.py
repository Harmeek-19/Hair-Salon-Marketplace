from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class URLTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token = request.query_params.get('token')
        if not token:
            return None

        try:
            user, _ = self.authenticate_credentials(token)
        except AuthenticationFailed:
            return None

        return (user, token)