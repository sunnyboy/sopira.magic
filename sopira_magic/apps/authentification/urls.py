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
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
]

