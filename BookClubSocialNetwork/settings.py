"""
Django settings for BookClubSocialNetwork project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

import environ

# Initialise environment variables
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # set to False on deployment to display user friendly 404

ALLOWED_HOSTS = []
# ALLOWED_HOSTS = ['.localhost'] # Uncomment this to see the user-friendly 404, and add current domain name to the list
                # e.g. 'novella-books.herokuapp.com'

# Application definition

INSTALLED_APPS = [
    'BookClub',
    'bulma',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'verify_email.apps.VerifyEmailConfig',
    'crispy_forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BookClubSocialNetwork.urls'

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
                'BookClub.form_processor.ForumPostForm',
                'BookClub.form_processor.BooklistContext'
            ],
        },
    },
]

WSGI_APPLICATION = 'BookClubSocialNetwork.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), ]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URL for redirecting users from login protected views
LOGIN_URL = 'login'

REDIRECT_URL_WHEN_LOGGED_IN = 'home'

AUTH_USER_MODEL = 'BookClub.User'

# Activate django_heroku
try:
    if '/app' in os.environ['HOME']:
        import django_heroku

        django_heroku.settings(locals())
except:
    if '/app' in os.path.expanduser('~'):
        import django_heroku

        django_heroku.settings(locals())

# SMTP Configuration
# For Django Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = env('EMAIL_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_PASSWORD')

EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = 'noreply<no_reply@domain.com>'

EXPIRE_AFTER = "1h" # Will expire after one hour from link generation

HTML_MESSAGE_TEMPLATE = 'account_verification/verification_email.html'
VERIFICATION_SUCCESS_TEMPLATE = None
VERIFICATION_FAILED_TEMPLATE = 'account_verification/verification_email_failed.html'
REQUEST_NEW_EMAIL_TEMPLATE = 'account_verification/verification_email_request.html'
LINK_EXPIRED_TEMPLATE = 'account_verification/verification_email_expired.html'
