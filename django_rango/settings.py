"""
Django settings for django_rango project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__)) # path to <project>/
TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')   # path to <project>/templates
STATIC_PATH = os.path.join(BASE_DIR, 'static')        # path to <project>/static



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j!6u1n%ihv!^coi44^ekn6xp1^thia72re9osm#$pen(05xb94'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rango',
    'registration',
    'rest_framework',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'django_rango.urls'

WSGI_APPLICATION = 'django_rango.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    STATIC_PATH,
)


# templates

TEMPLATE_DIRS = (
    TEMPLATE_PATH,
)


# media server

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Redirect users that aren't logged in.

LOGIN_URL = '/accounts/login/'


# Django-Registration-Redux settings

REGISTRATION_OPEN = True            # If True, users can register
ACCOUNT_ACTIVATION_DAYS = 7         # One-week activation window
REGISTRATION_AUTO_LOGIN = True      # If True, the user will be automatically logged in
LOGIN_REDIRECT_URL = '/rango/'      # The page you want users to arrive at after they successful log in
LOGIN_URL = '/accounts/login/'      # The page users are directed to if they are not logged in,
                                    # and are tying to access pages requiring authentication
