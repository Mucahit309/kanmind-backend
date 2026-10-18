"""Views for registration, login and email check."""
# 1. Third party
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# 2. Local imports
from .serializers import (
    EmailQuerySerializer,
    LoginSerializer,
    RegistrationSerializer,
    UserSummarySerializer,
)


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


class EmailCheckView(APIView):
    """Return the user that belongs to an email address."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Look up a user by the email query parameter."""
        query = EmailQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        email = query.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            raise NotFound("Email not found.")
        return Response(UserSummarySerializer(user).data)
