#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/serializers.py
#   Authentication Serializers - DRF serializers
#   Serializers for user registration, login, password reset, 2FA
#..............................................................

"""
Authentication Serializers - DRF Serializers.

   Django REST Framework serializers for authentication endpoints.
   Handles validation and serialization for user registration, login, and password operations.

   Serializers:

   1. UserRegistrationSerializer
      - Fields: username, email, password, password_confirm, first_name, last_name
      - Validates password match and strength
      - Creates user with hashed password

   2. LoginSerializer
      - Fields: username, password
      - Validates credentials

   3. PasswordResetSerializer
      - Fields: email
      - Initiates password reset process

   4. PasswordResetConfirmSerializer
      - Fields: uid, token, password, password_confirm
      - Validates token and resets password
      - Requires uid (base64-encoded user ID) and token from password reset email

   5. TwoFactorSerializer
      - Fields: code
      - Validates 2FA verification code

   Usage:
   ```python
   from sopira_magic.apps.authentification.serializers import UserRegistrationSerializer
   serializer = UserRegistrationSerializer(data=request.data)
   if serializer.is_valid():
       user = serializer.save()
   ```
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


class TwoFactorSerializer(serializers.Serializer):
    """Serializer for 2FA verification."""
    code = serializers.CharField(max_length=6)

