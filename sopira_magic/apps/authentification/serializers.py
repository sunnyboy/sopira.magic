#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/serializers.py
#   Authentication Serializers - DRF serializers
#   Serializers for user registration, login, password reset, 2FA
#..............................................................

"""
Authentication Serializers - Config-Driven DRF Serializers.

Django REST Framework serializers for authentication endpoints.
All validators use AUTH_CONFIG instead of hardcoded rules.

Serializers:
- UserRegistrationSerializer: Config-driven user registration
- LoginSerializer: Config-driven login validation
- PasswordResetSerializer: Config-driven password reset request
- PasswordResetConfirmSerializer: Config-driven password reset confirmation
- TwoFactorSerializer: Config-driven 2FA verification

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

from .validators import validate_password, validate_username, validate_email
from .config import get_validation_config


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration - config-driven."""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.Meta.model is None:
            self.Meta.model = get_user_model()
    
    class Meta:
        model = None  # Will be set dynamically in __init__
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
    
    def validate_username(self, value):
        """Validate username using AUTH_CONFIG."""
        is_valid, error = validate_username(value)
        if not is_valid:
            raise serializers.ValidationError(error)
        return value
    
    def validate_email(self, value):
        """Validate email using AUTH_CONFIG."""
        if value:  # Email is optional
            is_valid, error = validate_email(value)
            if not is_valid:
                raise serializers.ValidationError(error)
        return value
    
    def validate_password(self, value):
        """Validate password using AUTH_CONFIG."""
        is_valid, error = validate_password(value)
        if not is_valid:
            raise serializers.ValidationError(error)
        return value
    
    def validate(self, attrs):
        """Validate password match."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create user - actual creation done by AuthEngine."""
        validated_data.pop('password_confirm')
        # Note: Actual user creation is handled by AuthEngine.create_user()
        # This serializer is kept for backward compatibility but may not be used
        User = get_user_model()
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

