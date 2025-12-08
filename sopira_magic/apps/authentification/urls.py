#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/authentification/urls.py
#   Authentication URLs - URL routing
#   URL patterns for authentication endpoints
#..............................................................

"""
Authentication URLs - URL Routing.

   URL configuration for authentication endpoints.
   All routes are prefixed with /api/auth/ in main urls.py.

   URL Patterns:
   - register/ - User registration (POST)
   - login/ - User login (POST)
   - logout/ - User logout (POST)
   - password-reset/ - Request password reset (POST)
   - password-reset-confirm/ - Confirm password reset (POST)
   - verify-2fa/ - Two-factor authentication (POST)

   App Name: authentification
   Full URL examples:
   - /api/auth/register/
   - /api/auth/login/
   - /api/auth/logout/
"""

from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    # Config-driven endpoints
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('check/', views.check_auth_view, name='check_auth'),
    path('csrf/', views.csrf_token_view, name='csrf_token'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password_view, name='reset_password_with_token'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
]

