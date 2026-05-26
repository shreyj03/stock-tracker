"""
Django settings for stock_tracker project.
Production-ready: reads secrets and DATABASE_URL from environment variables.
Local dev falls back to SQLite when DATABASE_URL is not set.
"""

from pathlib import Path
import os
import dj_database_url

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
# Set SECRET_KEY in your Render environment variables (or .env locally).
# The insecure fallback is ONLY for running `manage.py` locally without a
# .env file — never deploy with it.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-local-dev-only-change-me-before-deploy',
)

# Set DEBUG=True in a local .env; Render should leave this unset (defaults False).
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    # Render assigns a hostname like <app-name>.onrender.com
    '.onrender.com',
]

# Allow overriding ALLOWED_HOSTS entirely via env (comma-separated list)
if os.environ.get('ALLOWED_HOSTS'):
    ALLOWED_HOSTS += [h.strip() for h in os.environ['ALLOWED_HOSTS'].split(',')]


# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'project',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must come right after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stock_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'project.context_processors.profile_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'stock_tracker.wsgi.application'


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# DATABASE_URL is set automatically by Render when you attach a PostgreSQL
# database. Locally, if DATABASE_URL is not set, we fall back to SQLite so
# you can run `manage.py runserver` without any extra setup.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static files  (WhiteNoise serves them in production)
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise: compress and cache-bust static files automatically
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ---------------------------------------------------------------------------
# Media files  (user-uploaded content — not served by WhiteNoise)
# ---------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------------------------
# Auth redirects
# ---------------------------------------------------------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
