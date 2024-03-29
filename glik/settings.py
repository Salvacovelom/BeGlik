"""
Django settings for glik project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from datetime import timedelta
from google.oauth2 import service_account
from pathlib import Path

# To get the environment variable
import os
from dotenv import load_dotenv
load_dotenv()

from glik.constants import ENVIRONMENT_NAMES

# google cloud storage

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-psdf6bp^dvg*omyhk$st_dk(qm^#=+)b!a#jl2i*3$8et%%ci0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "10.0.1.0/28",
    "127.0.0.1",
    os.environ.get("BACKEND_STAGING_URL"),
    os.environ.get("BACKEND_PRODUCTION_URL"),
    '*'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',  # To use TokenAuthentication
    'users',  # Our authentication app with the custom User model
    'authentication',
    'products',
    'leases',
    'payments',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # camel case
    'djangorestframework_camel_case.middleware.CamelCaseMiddleWare',
]

ROOT_URLCONF = 'glik.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'glik.wsgi.application'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # https://www.django-rest-framework.org/api-guide/authentication/#by-exposing-an-api-endpoint
        'rest_framework.authentication.TokenAuthentication',
    ],

    # https://github.com/vbabiy/djangorestframework-camel-case
    # Transform the response data to camel case
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
        # Any other renders
    ),
    # Transform the request data to camel case
    'DEFAULT_PARSER_CLASSES': (
        # If you use MultiPartFormParser or FormParser, we also have a camel case version
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
        # Any other parsers
    ),
    # Global exception  handler
    'EXCEPTION_HANDLER': 'exceptions.custom_exception_handler.custom_exception_handler'
}


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("POSTGRES_DB"),
        'USER': os.environ.get("POSTGRES_USER"),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
        'HOST': os.environ.get("POSTGRES_HOST"),
        'PORT': os.environ.get("POSTGRES_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es'  # 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')
MEDIA_URLS ='/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#auth-custom-user
AUTH_USER_MODEL = 'users.User'

#CORS_ALLOWED_ORIGINS = [
#    os.environ.get("ADMIN_BASE_URL"),
#    os.environ.get("WEB_BASE_URL"),
#    "*"
#]

#if os.environ.get("ENVIROMENT") == ENVIRONMENT_NAMES.CI.value:
#    CORS_ALLOWED_ORIGINS.append("http://localhost:3001")
#    CORS_ALLOWED_ORIGINS.append("http://localhost:3000")

ADMIN_ENABLED = False

# Email settings
# https://docs.sendgrid.com/for-developers/sending-email/django
EMAIL_HOST = os.environ.get("EMAIL_HOST", 'smtp.postmarkapp.com')
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", None)
EMAIL_PORT = os.environ.get("EMAIL_PORT", 587)
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", None)

# Google Cloud Storage
# https://django-storages.readthedocs.io/en/latest/backends/gcloud.html#settings
GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")
# DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.environ.get("GS_CREDENTIALS_FILE_PATH")
)
GS_EXPIRATION = timedelta(minutes=5)
# Needed for uploading large streams, entirely optional otherwise
GS_BLOB_CHUNK_SIZE = 1024 * 256 * 40
STORAGES = {"default": {
    "BACKEND": "storages.backends.gcloud.GoogleCloudStorage"}}
