#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/engine.py
#   Authentication Engine - Config-driven authentication logic
#   Main authentication engine using AUTH_CONFIG and registry callbacks
#..............................................................

"""
Authentication Engine - Config-Driven Authentication Logic.

Main authentication engine that uses AUTH_CONFIG instead of hardcoded logic.
All authentication operations are driven by configuration and registry callbacks.

Usage:
```python
from sopira_magic.apps.authentification.engine import AuthEngine
user = AuthEngine.authenticate_user(request, username, password)
```
"""

import logging
from typing import Any, Dict, Optional

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpRequest

from .config import (
    AUTH_CONFIG,
    get_auth_config,
    is_endpoint_enabled,
    get_audit_config,
    get_notification_config,
    get_session_config,
)
from .registry import (
    get_audit_logger,
    get_notification_sender,
    get_user_serializer,
    get_role_provider,
)
from .validators import validate_password, validate_username, validate_email
from .types import AuthAction

logger = logging.getLogger(__name__)


def _get_user_model():
    """Get user model - lazy import to avoid AppRegistryNotReady."""
    return get_user_model()


def _get_ip_address(request: HttpRequest) -> str:
    """Get client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "Unknown")


def _get_user_agent(request: HttpRequest) -> str:
    """Get user agent from request."""
    return request.META.get("HTTP_USER_AGENT", "Unknown")


def _serialize_user(user: Any) -> Dict[str, Any]:
    """Serialize user data using registry callback or default."""
    serializer = get_user_serializer()
    if serializer:
        return serializer(user)

    # Default serialization
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


def _get_role_data(user: Any) -> Dict[str, Any]:
    """Get role data using registry callback or default."""
    provider = get_role_provider()
    if provider:
        return provider(user)

    # Default role data (using User.role field)
    role = getattr(user, "role", "READER")
    return {
        "role": role,
        "role_display": role,
        "role_priority": 0,
        "is_admin": user.is_staff or user.is_superuser,
        "is_superuser_role": user.is_superuser,
    }


def _log_audit(action: str, user: Optional[Any] = None, success: bool = True, **kwargs) -> None:
    """Log audit event using registry callback."""
    audit_config = get_audit_config()
    if not audit_config.get("audit_enabled", False):
        return

    audit_actions = audit_config.get("audit_actions", [])
    if action not in [a.value if hasattr(a, "value") else a for a in audit_actions]:
        return

    logger_callback = get_audit_logger()
    if logger_callback:
        try:
            logger_callback(action, user, success=success, **kwargs)
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")
    else:
        # Default logging
        logger.info(f"Auth audit: {action} - User: {user} - Success: {success} - {kwargs}")


def _send_notification(notification_type: str, data: Dict[str, Any]) -> None:
    """Send notification using registry callback."""
    notification_config = get_notification_config()
    if not notification_config.get("notifications_enabled", False):
        return

    notification_config_for_type = notification_config.get(notification_type, {})
    if not notification_config_for_type.get("enabled", False):
        return

    sender = get_notification_sender()
    if sender:
        try:
            sender(notification_type, data)
        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
    else:
        logger.debug(f"Notification {notification_type} would be sent: {data}")


class AuthEngine:
    """Authentication Engine - SINGLE SOURCE OF TRUTH for authentication decisions.

    All authentication logic is driven by AUTH_CONFIG and registry callbacks.
    No hardcoded domain-specific logic.
    """

    @classmethod
    def authenticate_user(
        cls, request: HttpRequest, username: str, password: str
    ) -> Optional[Any]:
        """Authenticate user using AUTH_CONFIG.

        Args:
            request: Django request object
            username: Username
            password: Password

        Returns:
            User object if authenticated, None otherwise
        """
        if not is_endpoint_enabled("login"):
            logger.warning("Login endpoint is disabled")
            return None

        login_config = get_auth_config("login")
        if not login_config:
            logger.error("Login config not found")
            return None

        # Validate username
        is_valid, error = validate_username(username)
        if not is_valid:
            logger.warning(f"Invalid username: {error}")
            return None

        # Authenticate
        logger.debug(f"Calling Django authenticate() with username: {username}")
        user = authenticate(request, username=username, password=password)
        logger.debug(f"Django authenticate() returned: {user}")

        if user:
            # Log successful login
            _log_audit(
                AuthAction.LOGIN.value,
                user=user,
                success=True,
                ip_address=_get_ip_address(request),
                user_agent=_get_user_agent(request),
            )

            # Send login notification
            from django.utils import timezone
            _send_notification(
                "login_notification",
                {
                    "user": user,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role if hasattr(user, 'role') else 'READER',
                    "timestamp": timezone.now().strftime('%d.%m.%Y %H:%M:%S'),
                    "ip_address": _get_ip_address(request),
                    "user_agent": _get_user_agent(request),
                },
            )

            return user
        else:
            # Log failed login
            _log_audit(
                AuthAction.LOGIN_FAILED.value,
                user=None,
                success=False,
                username=username,
                ip_address=_get_ip_address(request),
                user_agent=_get_user_agent(request),
            )

        return None

    @classmethod
    def create_user(cls, request: HttpRequest, user_data: Dict[str, Any]) -> Any:
        """Create new user using AUTH_CONFIG.

        Args:
            request: Django request object
            user_data: User data dictionary

        Returns:
            Created User object

        Raises:
            ValueError: If validation fails
        """
        if not is_endpoint_enabled("signup"):
            raise ValueError("Signup endpoint is disabled")

        signup_config = get_auth_config("signup")
        if not signup_config:
            raise ValueError("Signup config not found")

        username = user_data.get("username")
        password = user_data.get("password")
        email = user_data.get("email", "")
        first_name = user_data.get("first_name", "")
        last_name = user_data.get("last_name", "")

        # Validate username
        is_valid, error = validate_username(username)
        if not is_valid:
            raise ValueError(f"Invalid username: {error}")

        # Validate password
        is_valid, error = validate_password(password)
        if not is_valid:
            raise ValueError(f"Invalid password: {error}")

        # Validate email if provided
        if email:
            is_valid, error = validate_email(email)
            if not is_valid:
                raise ValueError(f"Invalid email: {error}")

        # Check if user already exists
        User = _get_user_model()
        if User.objects.filter(username=username).exists():
            raise ValueError("User with this username already exists")

        if email and User.objects.filter(email=email).exists():
            raise ValueError("User with this email already exists")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Set default role
        default_role = signup_config.get("default_role", "READER")
        if hasattr(user, "role"):
            user.role = default_role
            user.save()

        # Log signup
        _log_audit(
            AuthAction.SIGNUP.value,
            user=user,
            success=True,
            ip_address=_get_ip_address(request),
            user_agent=_get_user_agent(request),
        )

        # Send signup notification
        _send_notification(
            "signup_notification",
            {
                "user": user,
                "ip_address": _get_ip_address(request),
                "user_agent": _get_user_agent(request),
            },
        )

        # Auto-login if configured
        if signup_config.get("auto_login", False):
            login(request, user)

        return user

    @classmethod
    def reset_password(cls, request: HttpRequest, email: str) -> Dict[str, Any]:
        """Request password reset using AUTH_CONFIG.

        Args:
            request: Django request object
            email: User email

        Returns:
            Dictionary with result (success, message, uid, token)
        """
        if not is_endpoint_enabled("password_reset"):
            return {"success": False, "error": "Password reset endpoint is disabled"}

        password_reset_config = get_auth_config("password_reset")
        if not password_reset_config:
            return {"success": False, "error": "Password reset config not found"}

        User = _get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists (security)
            return {
                "success": True,
                "message": "If an account with this email exists, a password reset link has been sent.",
            }

        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Log password reset request
        _log_audit(
            AuthAction.PASSWORD_RESET.value,
            user=user,
            success=True,
            ip_address=_get_ip_address(request),
            user_agent=_get_user_agent(request),
        )

        # Send password reset notification
        reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"
        _send_notification(
            "password_reset_notification",
            {
                "user": user,
                "reset_link": reset_link,
                "token": token,
                "uid": uid,
            },
        )

        return {
            "success": True,
            "message": "If an account with this email exists, a password reset link has been sent.",
            "uid": uid,
            "token": token,  # In production, don't return token
        }

    @classmethod
    def confirm_password_reset(
        cls, request: HttpRequest, uid: str, token: str, new_password: str
    ) -> bool:
        """Confirm password reset using AUTH_CONFIG.

        Args:
            request: Django request object
            uid: Base64-encoded user ID
            token: Password reset token
            new_password: New password

        Returns:
            True if password reset successful, False otherwise
        """
        if not is_endpoint_enabled("password_reset_confirm"):
            return False

        password_reset_confirm_config = get_auth_config("password_reset_confirm")
        if not password_reset_confirm_config:
            return False

        # Validate password
        is_valid, error = validate_password(new_password)
        if not is_valid:
            logger.warning(f"Invalid password: {error}")
            return False

        # Decode user ID
        User = _get_user_model()
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return False

        # Verify token
        if not default_token_generator.check_token(user, token):
            return False

        # Reset password
        user.set_password(new_password)
        user.save()

        # Log password reset confirm
        _log_audit(
            AuthAction.PASSWORD_RESET_CONFIRM.value,
            user=user,
            success=True,
            ip_address=_get_ip_address(request),
            user_agent=_get_user_agent(request),
        )

        return True

    @classmethod
    def verify_2fa(cls, request: HttpRequest, user: Any, code: str) -> bool:
        """Verify 2FA code using AUTH_CONFIG.

        Args:
            request: Django request object
            user: User object
            code: 2FA code

        Returns:
            True if 2FA verified, False otherwise
        """
        if not is_endpoint_enabled("verify_2fa"):
            return False

        verify_2fa_config = get_auth_config("verify_2fa")
        if not verify_2fa_config:
            return False

        # TODO: Implement 2FA verification logic
        logger.warning("2FA verification not implemented yet")
        return False

    @classmethod
    def check_authentication(cls, request: HttpRequest) -> Dict[str, Any]:
        """Check authentication status using AUTH_CONFIG.

        Args:
            request: Django request object

        Returns:
            Dictionary with authentication status and user data
        """
        if not is_endpoint_enabled("check_auth"):
            return {"authenticated": False}

        check_auth_config = get_auth_config("check_auth")
        if not check_auth_config:
            return {"authenticated": False}

        if request.user.is_authenticated:
            user_data = _serialize_user(request.user)

            # Add role data if configured
            if check_auth_config.get("include_permissions", False):
                role_data = _get_role_data(request.user)
                user_data.update(role_data)

            return {
                "authenticated": True,
                "user": user_data,
            }

        return {"authenticated": False}

    @classmethod
    def logout_user(cls, request: HttpRequest) -> bool:
        """Logout user using AUTH_CONFIG.

        Args:
            request: Django request object

        Returns:
            True if logout successful, False otherwise
        """
        if not is_endpoint_enabled("logout"):
            return False

        logout_config = get_auth_config("logout")
        if not logout_config:
            return False

        user = request.user if request.user.is_authenticated else None

        # Log logout
        if user:
            _log_audit(
                AuthAction.LOGOUT.value,
                user=user,
                success=True,
                ip_address=_get_ip_address(request),
                user_agent=_get_user_agent(request),
            )

        # Logout
        logout(request)

        return True

