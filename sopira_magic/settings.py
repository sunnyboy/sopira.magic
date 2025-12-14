#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/settings.py
#   Django Settings - Main project configuration
#   Environment-aware settings with multi-database support
#..............................................................

"""
   Django Settings - Main Project Configuration.

   Central configuration file for sopira.magic Django project.
   Handles environment detection, multi-database setup, security, and app registration.

   Key Features:
   - Environment-aware configuration (local/dev/production/render)
   - Multi-database architecture (PRIMARY, STATE, LOGGING)
   - Intelligent security configuration via security_config module
   - All 35 Django apps registered and configured
   - REST Framework, CORS, and middleware configuration

   Database Architecture:
   - default (PRIMARY): Business data storage (user, company, factory, etc.)
   - state: UI state persistence and user preferences
   - logging: Application logs and audit trails

   Security:
   - CORS and CSRF automatically configured based on environment
   - Session and cookie settings adapt to environment
   - SSL/TLS enforcement in production environments

   Apps Structure:
   - Core: core, shared
   - User & Auth: user, authentification
   - Business Logic: company, factory, productionline, equipment, etc.
   - Services: search, notification, reporting, analytics, etc.
   - SSOT & Config-driven: relation, generator
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Import intelligent security configuration
from .security_config import (
    get_cors_origins,
    get_csrf_trusted_origins,
    get_session_cookie_settings,
    get_csrf_cookie_settings,
    detect_environment,
    get_elasticsearch_config,
)

# -----------------------------------------------------------------------------
# ZÁKLAD
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env", override=False)

# Prostredie a debug prepínač
ENV = os.getenv("ENV", "local")
DEBUG = os.getenv("DEBUG", "1" if ENV == "local" else "0") == "1"

# DEV: Skip API authentication for browser testing (disabled by default)
DEV_SKIP_AUTH = os.getenv("DEV_SKIP_AUTH", "0") == "1"

# Secret key
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-secret-key-change-in-production")

# Povolené hosty
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost,testserver").split(",")

# Intelligent CSRF trusted origins - automatically configured based on environment
CSRF_TRUSTED_ORIGINS = get_csrf_trusted_origins()

# -----------------------------------------------------------------------------
# APLIKÁCIE
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "corsheaders",
    "rest_framework",
    "django_filters",

    # Sopira.magic apps - Core
    "sopira_magic.apps.core",
    "sopira_magic.apps.shared",
    "sopira_magic.apps.security",
    
    # User & Auth
    "sopira_magic.apps.m_user",
    "sopira_magic.apps.authentification",
    
    # Business Logic
    "sopira_magic.apps.m_company",
    "sopira_magic.apps.m_factory",
    "sopira_magic.apps.m_location",
    "sopira_magic.apps.m_carrier",
    "sopira_magic.apps.m_driver",
    "sopira_magic.apps.m_pot",
    "sopira_magic.apps.m_pit",
    "sopira_magic.apps.m_machine",
    "sopira_magic.apps.m_camera",
    "sopira_magic.apps.m_measurement",
    "sopira_magic.apps.m_productionline",
    "sopira_magic.apps.m_utility",
    "sopira_magic.apps.m_equipment",
    "sopira_magic.apps.m_resource",
    "sopira_magic.apps.m_worker",
    "sopira_magic.apps.m_material",
    "sopira_magic.apps.m_process",
    "sopira_magic.apps.endpoint",
    "sopira_magic.apps.dashboard",
    
    # Services
    "sopira_magic.apps.search",
    "sopira_magic.apps.notification",
    "sopira_magic.apps.reporting",
    "sopira_magic.apps.analytics",
    "sopira_magic.apps.alarm",
    "sopira_magic.apps.audit",
    "sopira_magic.apps.logging",
    "sopira_magic.apps.file_storage",
    "sopira_magic.apps.m_document",
    "sopira_magic.apps.m_video",
    "sopira_magic.apps.m_photo",
    "sopira_magic.apps.m_tag",
    "sopira_magic.apps.scheduler",
    "sopira_magic.apps.fk_options_cache",
    "sopira_magic.apps.mystate",  # New state management module
    "sopira_magic.apps.internationalization",
    "sopira_magic.apps.impex",
    "sopira_magic.apps.api",
    "sopira_magic.apps.mobileapp",
    
    # SSOT & Config-driven
    "sopira_magic.apps.accessrights",
    "sopira_magic.apps.relation",
    "sopira_magic.apps.generator",
    "sopira_magic.apps.pdfviewer",
    "sopira_magic.apps.scoping",
]

# -----------------------------------------------------------------------------
# MIDDLEWARE
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "sopira_magic.apps.security.middleware.SecurityMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # X-Frame-Options disabled for local dev PDF viewing in iframe
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    # 🔍 TEMPORARY: DB Watchdog - sleduje DB query count per request
    "sopira_magic.middleware_db_debug.DatabaseDebugMiddleware",
]

ROOT_URLCONF = "sopira_magic.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sopira_magic.wsgi.application"

# -----------------------------------------------------------------------------
# DATABÁZA - MULTI-DATABASE ARCHITECTURE
# -----------------------------------------------------------------------------
# PRIMARY DATABASE: Hlavné business data storage
# STATE DATABASE: UI state a user preferences
# LOGGING DATABASE: Application logs a audit trails

PRIMARY_DATABASE_URL = os.getenv("PRIMARY_DATABASE_URL", os.getenv("DATABASE_URL", "postgresql://localhost/sopira_magic"))
STATE_DATABASE_URL = os.getenv("STATE_DATABASE_URL", "postgresql://localhost/sopira_magic_state")
LOGGING_DATABASE_URL = os.getenv("LOGGING_DATABASE_URL", "postgresql://localhost/sopira_magic_logging")

DATABASES = {
    "default": dj_database_url.config(
        default=PRIMARY_DATABASE_URL,
        conn_max_age=600,
        ssl_require=(os.getenv("ENV") == "render"),
    ),
    "state": dj_database_url.config(
        default=STATE_DATABASE_URL,
        conn_max_age=600,
        ssl_require=(os.getenv("ENV") == "render"),
    ),
    "logging": dj_database_url.config(
        default=LOGGING_DATABASE_URL,
        conn_max_age=600,
        ssl_require=(os.getenv("ENV") == "render"),
    ),
}

# Force connection pooling for all databases
for db_name in DATABASES:
    if 'CONN_MAX_AGE' not in DATABASES[db_name] and 'conn_max_age' in DATABASES[db_name]:
        DATABASES[db_name]['CONN_MAX_AGE'] = DATABASES[db_name]['conn_max_age']
    elif 'CONN_MAX_AGE' not in DATABASES[db_name]:
        # 🔧 ZNÍŽENÉ z 600 na 30 sekúnd - prevents connection slot exhaustion
        DATABASES[db_name]['CONN_MAX_AGE'] = 30

# Database router
DATABASE_ROUTERS = ['sopira_magic.db_router.DatabaseRouter']

# -----------------------------------------------------------------------------
# PASSWORD VALIDATION
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# -----------------------------------------------------------------------------
# LOKALIZÁCIA
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# STATICKÉ SÚBORY
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -----------------------------------------------------------------------------
# MÉDIÁ
# -----------------------------------------------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------------------------------------------------------
# CORS / CSRF
# -----------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = get_cors_origins()
CORS_ALLOW_CREDENTIALS = True

# -----------------------------------------------------------------------------
# BEZPEČNOSŤ
# -----------------------------------------------------------------------------
# Nastavenia pre nový security modul (ConfigDriven & SSOT)
SECURITY_VALIDATE_ON_STARTUP = os.getenv("SECURITY_VALIDATE_ON_STARTUP", "1") == "1"
SECURITY_AUDIT_ON_STARTUP = os.getenv("SECURITY_AUDIT_ON_STARTUP", "0") == "1"

env_type, is_https, is_localhost = detect_environment()

# Session cookie settings
session_cookie_settings = get_session_cookie_settings()
if "SESSION_COOKIE_SAMESITE" in session_cookie_settings:
    SESSION_COOKIE_SAMESITE = session_cookie_settings["SESSION_COOKIE_SAMESITE"]
SESSION_COOKIE_SECURE = session_cookie_settings["SESSION_COOKIE_SECURE"]
SESSION_COOKIE_HTTPONLY = session_cookie_settings["SESSION_COOKIE_HTTPONLY"]

# CSRF cookie settings
csrf_cookie_settings = get_csrf_cookie_settings()
if "CSRF_COOKIE_SAMESITE" in csrf_cookie_settings:
    CSRF_COOKIE_SAMESITE = csrf_cookie_settings["CSRF_COOKIE_SAMESITE"]
CSRF_COOKIE_SECURE = csrf_cookie_settings["CSRF_COOKIE_SECURE"]
CSRF_COOKIE_HTTPONLY = csrf_cookie_settings["CSRF_COOKIE_HTTPONLY"]

# Production-specific security settings
if env_type in ["production", "render"]:
    if env_type == "render":
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -----------------------------------------------------------------------------
# SEARCH SERVICE (Elasticsearch)
# -----------------------------------------------------------------------------
_es_cfg = get_elasticsearch_config()
ELASTICSEARCH_URL = _es_cfg["url"]
SEARCH_ELASTIC_ENABLED = _es_cfg["enabled"]
SEARCH_INDEX_PREFIX = _es_cfg["index_prefix"]
SEARCH_DEFAULT_MODE = _es_cfg["default_mode"]  # simple | advanced
SEARCH_ALLOW_APPROX = _es_cfg["allow_approx"]
SEARCH_REQUEST_TIMEOUT = _es_cfg["request_timeout"]
SEARCH_MAX_PAGE_SIZE = _es_cfg["max_page_size"]
ELASTICSEARCH_CA_CERT = os.getenv("ELASTICSEARCH_CA_CERT")
ELASTICSEARCH_VERIFY_CERTS = os.getenv("ELASTICSEARCH_VERIFY_CERTS", "0") == "1"

# -----------------------------------------------------------------------------
# DEFAULT PRIMARY KEY
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------------
# AUTH USER MODEL
# -----------------------------------------------------------------------------
AUTH_USER_MODEL = "user.User"

# -----------------------------------------------------------------------------
# LOGGING
# -----------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'sopira_magic.apps.generator': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'sopira_magic.apps.authentification': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# -----------------------------------------------------------------------------
# EMAIL CONFIGURATION
# -----------------------------------------------------------------------------
# Gmail SMTP configuration (migrated from Thermal Eye)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True  # Use TLS port 587
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 30
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # Your Gmail address
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # App password (not regular password)
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', 'noreply@sopira.com')

# SSL Context for Mac OS (fix certificate issues)
import ssl
if hasattr(ssl, '_create_default_https_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# Admin email for notifications
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'sopira@me.com')

# For development, you can use console backend to see emails in console
# Uncomment below if you want to test without sending real emails:
# if DEBUG and ENV == "local":
#     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# -----------------------------------------------------------------------------
# REST FRAMEWORK
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
}
