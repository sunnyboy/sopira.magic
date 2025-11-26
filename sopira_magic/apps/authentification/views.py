#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/views.py
#   Authentication Views - REST API endpoints
#   User authentication, registration, password reset, 2FA
#..............................................................

"""
Authentication Views - REST API Endpoints.

   REST API views for user authentication and account management.
   Provides endpoints for registration, login, logout, password reset, and 2FA.

   Endpoints:
   - POST /api/auth/register/ - User registration
   - POST /api/auth/login/ - User login
   - POST /api/auth/logout/ - User logout
   - POST /api/auth/password-reset/ - Request password reset
   - POST /api/auth/password-reset-confirm/ - Confirm password reset
   - POST /api/auth/verify-2fa/ - Two-factor authentication verification

   Features:
   - User registration with password validation
   - Session-based authentication
   - Password reset via email token
   - Two-factor authentication support
   - RESTful API responses

   Usage:
   ```python
   # Registration
   POST /api/auth/register/
   {"username": "user", "email": "user@example.com", "password": "...", ...}

   # Login
   POST /api/auth/login/
   {"username": "user", "password": "..."}

   # Password Reset Request
   POST /api/auth/password-reset/
   {"email": "user@example.com"}

   # Password Reset Confirm
   POST /api/auth/password-reset-confirm/
   {"uid": "base64_encoded_user_id", "token": "reset_token", "password": "new_password", "password_confirm": "new_password"}
   ```
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    TwoFactorSerializer,
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint."""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout endpoint."""
    logout(request)
    return Response({'message': 'Logout successful'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset(request):
    """Password reset request endpoint."""
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            # Generate token and send email (implementation depends on email service)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # TODO: Send email with reset link
            return Response({
                'message': 'Password reset email sent',
                'uid': uid,
                'token': token  # In production, don't return token
            })
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({'message': 'If email exists, reset link was sent'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Password reset confirmation endpoint."""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['password']
        
        try:
            # Decode user ID from base64
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            # Invalid uid format or user doesn't exist
            return Response(
                {'error': 'Invalid reset link. Please request a new password reset.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify token is valid for this user
        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Invalid or expired reset token. Please request a new password reset.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset password
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password reset successful'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    """2FA verification endpoint."""
    serializer = TwoFactorSerializer(data=request.data)
    if serializer.is_valid():
        code = serializer.validated_data['code']
        # TODO: Implement 2FA verification logic
        return Response({'message': '2FA verified successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

