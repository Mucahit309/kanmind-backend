"""Serializers for registration and login."""
# 1. Standard library
# (none)

# 2. Third party
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a new user."""

    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        """Ensure the email is not used yet (case-insensitive)."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value.lower()

    def validate(self, attrs):
        """Ensure both passwords are identical."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create the user with the email as username."""
        email = validated_data["email"]
        return User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            first_name=validated_data["fullname"],
        )


class LoginSerializer(serializers.Serializer):
    """Validate credentials and attach the authenticated user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the user by email and password."""
        user = authenticate(
            username=attrs["email"].lower(),
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        attrs["user"] = user
        return attrs
