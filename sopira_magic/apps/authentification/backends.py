#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/backends.py
#   Authentication Backends - Custom auth backends
#   Email-based authentication backend
#..............................................................

"""
Authentication Backends - Custom Auth Backends.

   Custom Django authentication backends for alternative authentication methods.
   Provides email-based authentication in addition to username-based.

   Backends:

   EmailBackend (extends ModelBackend)
   - Authenticates users using email instead of username
   - Allows login with email + password
   - Falls back to standard ModelBackend behavior

   Configuration:
   Add to settings.py AUTHENTICATION_BACKENDS:
   AUTHENTICATION_BACKENDS = [
       'sopira_magic.apps.authentification.backends.EmailBackend',
       'django.contrib.auth.backends.ModelBackend',
   ]

   Usage:
   ```python
   from django.contrib.auth import authenticate
   user = authenticate(request, username='user@example.com', password='password')
   ```
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    """Authentication backend using email instead of username."""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        
        if username is None or password is None:
            return None
        
        User = get_user_model()
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

