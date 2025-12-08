#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/views.py
#   Authentication Views - REST API endpoints
#   Config-driven authentication views using AuthEngine
#..............................................................

"""
Authentication Views - Config-Driven REST API Endpoints.

REST API views for user authentication and account management.
All views use AuthEngine and AUTH_CONFIG - no hardcoded logic.

Endpoints:
- POST /api/auth/signup/ - User registration (config-driven)
- POST /api/auth/login/ - User login (config-driven)
- POST /api/auth/logout/ - User logout (config-driven)
- GET /api/auth/check/ - Check authentication status (config-driven)
- GET /api/auth/csrf/ - Get CSRF token (config-driven)
- POST /api/auth/password-reset/ - Request password reset (config-driven)
- POST /api/auth/password-reset-confirm/ - Confirm password reset (config-driven)
- POST /api/auth/verify-2fa/ - Two-factor authentication (config-driven)

Features:
- Config-driven authentication (AUTH_CONFIG)
- AuthEngine for all authentication logic
- Registry callbacks for audit and notifications
- RESTful API responses

Usage:
```python
# Registration
POST /api/auth/signup/
{"username": "user", "email": "user@example.com", "password": "...", ...}

# Login
POST /api/auth/login/
{"username": "user", "password": "..."}

# Check Auth
GET /api/auth/check/

# CSRF Token
GET /api/auth/csrf/
```
"""

import json
import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

from .engine import AuthEngine
from .registry import get_user_serializer, get_role_provider
from .config import is_endpoint_enabled

logger = logging.getLogger(__name__)


def _serialize_user(user):
    """Serialize user data using registry callback or default."""
    serializer = get_user_serializer()
    if serializer:
        return serializer(user)

    # Default serialization
    role_data = {}
    provider = get_role_provider()
    if provider:
        role_data = provider(user)
    else:
        # Default role data
        role = getattr(user, "role", "READER")
        role_data = {
            "role": role,
            "role_display": role,
            "role_priority": 0,
            "is_admin": user.is_staff or user.is_superuser,
            "is_superuser_role": user.is_superuser,
        }

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        **role_data,
    }


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt  # CSRF handled via cookies and X-CSRFToken header
def signup_view(request):
    """User registration endpoint - config-driven."""
    if not is_endpoint_enabled("signup"):
        return Response(
            {'error': 'Signup endpoint is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use AuthEngine to create user
        try:
            user = AuthEngine.create_user(request, {
                'username': username,
                'password': password,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Serialize user data
        user_data = _serialize_user(user)

        return Response({
            'success': True,
            'user': user_data,
            'csrf_token': get_token(request)
        }, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        return Response(
            {'error': f'Registration error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt  # CSRF handled via cookies and X-CSRFToken header
def login_view(request):
    """User login endpoint - config-driven."""
    if not is_endpoint_enabled("login"):
        return Response(
            {'error': 'Login endpoint is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        # Parse request body - handle both bytes and string
        if request.content_type and 'application/json' in request.content_type:
            body = request.body
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            data = json.loads(body)
        else:
            data = request.POST
        
        username = data.get('username')
        password = data.get('password')

        logger.debug(f"Login attempt - username: {username}, content_type: {request.content_type}, body: {request.body}")

        if not username or not password:
            logger.warning(f"Login failed - missing username or password")
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use AuthEngine to authenticate
        logger.debug(f"Calling AuthEngine.authenticate_user for username: {username}")
        user = AuthEngine.authenticate_user(request, username, password)
        logger.debug(f"AuthEngine.authenticate_user returned: {user}")

        if user:
            login(request, user)
            user_data = _serialize_user(user)

            return Response({
                'success': True,
                'user': user_data,
                'csrf_token': get_token(request)
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid login credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return Response(
            {'error': f'Login error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout endpoint - config-driven."""
    if not is_endpoint_enabled("logout"):
        return Response(
            {'error': 'Logout endpoint is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    success = AuthEngine.logout_user(request)
    if success:
        return Response({
            'success': True,
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Logout failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def check_auth_view(request):
    """Check authentication status endpoint - config-driven."""
    if not is_endpoint_enabled("check_auth"):
        return Response(
            {'authenticated': False},
            status=status.HTTP_200_OK
        )

    result = AuthEngine.check_authentication(request)
    result['csrf_token'] = get_token(request)
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token_view(request):
    """Get CSRF token endpoint - config-driven."""
    return Response({
        'csrf_token': get_token(request)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def forgot_password_view(request):
    """Password reset request endpoint - config-driven."""
    if not is_endpoint_enabled("password_reset"):
        return Response(
            {'error': 'Password reset endpoint is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        email = data.get('email')

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use AuthEngine to reset password
        result = AuthEngine.reset_password(request, email)

        if result.get('success'):
            return Response({
                'success': True,
                'message': result.get('message', 'Password reset email sent')
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': result.get('error', 'Password reset failed')},
                status=status.HTTP_400_BAD_REQUEST
            )

    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Password reset error: {e}", exc_info=True)
        return Response(
            {'error': f'Error processing request: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def reset_password_view(request, uidb64=None, token=None):
    """Password reset confirmation endpoint - config-driven."""
    if not is_endpoint_enabled("password_reset_confirm"):
        return Response(
            {'error': 'Password reset confirm endpoint is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        password = data.get('password')

        # Get uid and token from URL or request body
        uid = uidb64 or data.get('uid')
        token = token or data.get('token')

        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not uid or not token:
            return Response(
                {'error': 'UID and token are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use AuthEngine to confirm password reset
        success = AuthEngine.confirm_password_reset(request, uid, token, password)

        if success:
            return Response({
                'success': True,
                'message': 'Password has been reset successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid or expired reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Password reset confirm error: {e}", exc_info=True)
        return Response(
            {'error': f'Error resetting password: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    """2FA verification endpoint - config-driven."""
    if not is_endpoint_enabled("verify_2fa"):
        return Response(
            {'error': '2FA endpoint is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        code = data.get('code')

        if not code:
            return Response(
                {'error': '2FA code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use AuthEngine to verify 2FA
        success = AuthEngine.verify_2fa(request, request.user, code)

        if success:
            return Response({
                'success': True,
                'message': '2FA verified successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid 2FA code'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"2FA verification error: {e}", exc_info=True)
        return Response(
            {'error': f'2FA verification error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

