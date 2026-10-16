"""Views for registration and login."""
# 1. Standard library
# (none)

# 2. Third party
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# 3. Local imports
from .serializers import LoginSerializer, RegistrationSerializer


def build_auth_payload(user):
    """Return token and user data after successful authentication."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "fullname": user.first_name,
        "email": user.email,
        "user_id": user.id,
    }


class RegistrationView(GenericAPIView):
    """Create a new user and return a token (no permissions required)."""

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Register a user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            build_auth_payload(user), status=status.HTTP_201_CREATED
        )


class LoginView(GenericAPIView):
    """Authenticate a user and return a token (no permissions required)."""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Log a user in."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response(build_auth_payload(user), status=status.HTTP_200_OK)
