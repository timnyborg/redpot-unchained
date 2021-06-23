"""
Django settings for redpot project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import json
import os
from pathlib import Path

import ldap
import sentry_sdk
from django_auth_ldap.config import LDAPSearch
from sentry_sdk.integrations.django import DjangoIntegration

from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# The secrets approach needs real work.  Hopefully something will work for python & env-based (docker)
try:
    with open(os.path.join(BASE_DIR, 'secrets.json')) as secrets_file:
        secrets = json.load(secrets_file)
except FileNotFoundError:
    secrets = {}


def get_secret(setting, default=None):
    """Get secret setting or fail with ImproperlyConfigured"""
    if setting in secrets:
        return secrets[setting]
    if default is not None:
        return default
    raise ImproperlyConfigured("Set the {} setting".format(setting))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret('DJANGO_SECRET_KEY', default=get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: don't run with allowed_hosts * in production!
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = get_secret('ALLOWED_HOSTS')

# Sentry integration
sentry_sdk.init(
    dsn=get_secret("SENTRY_DSN", ''),
    integrations=[DjangoIntegration()],
    environment='dev' if DEBUG else 'prod',
    # You may wish to set the sample_rate to 1.0 in dev, but it should be scaled much lower in production
    traces_sample_rate=get_secret("SENTRY_SAMPLE_RATE", 1),
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)

# Application definition
PREREQ_APPS = [
    'dal',  # django-autocomplete-light
    'dal_select2',  # django-autocomplete-light
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions', # disabled until migrated
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd party apps
    'menu',  # django-simple-menu
    'django_tables2',
    'django_filters',
    'widget_tweaks',  # django-widget-tweaks
    'celery_progress',
    'django_celery_beat',
    'django_celery_results',
]

PROJECT_APPS = [
    'apps.core',
    'apps.application',
    'apps.discount',
    'apps.enrolment',
    'apps.fee',
    'apps.hesa',
    'apps.invoice',
    'apps.module',
    'apps.programme',
    'apps.qualification_aim',
    'apps.student',
    'apps.tutor',
    'apps.tutor_payment',
    'apps.user',
]

INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS

if get_secret('REDIS_HOST', ''):
    CACHES = {
        # To separate redis session (semi-persistent) and redis cache (ephemeral), we could define a second
        #  cache (key: session), point it to another port/instance and use it as the SESSION_CACHE_ALIAS
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": 'redis://%s:%s' % (get_secret('REDIS_HOST'), get_secret('REDIS_PORT', 6379)),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PASSWORD": get_secret('REDIS_PASSWORD', ''),
            },
        }
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

else:
    # Use file-based sessions for CI/CD testing.  We may want to add a redis service to the pipelines in future
    SESSION_ENGINE = 'django.contrib.sessions.backends.file'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'redpot.urls'

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

WSGI_APPLICATION = 'redpot.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    # Default credentials only used against the test database created as part of CI
    'default': {
        'NAME': get_secret('DB_NAME', 'redpot'),
        'ENGINE': 'mssql',
        'HOST': get_secret('DB_HOST', 'mssql'),
        'USER': get_secret('DB_USER', 'sa'),
        'PASSWORD': get_secret('DB_PASSWORD', 'Test@only'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}

MESSAGE_TAGS = {
    # Overriding the error tag to match bootstrap 3
    messages.ERROR: 'danger'
}

AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",  # To enable groups & permissions
]

AUTH_LDAP_SERVER_URI = get_secret('LDAP_HOST', '')
AUTH_LDAP_BIND_DN = get_secret('LDAP_BIND_DN', '%s') % get_secret('LDAP_USER', '')
AUTH_LDAP_BIND_PASSWORD = get_secret('LDAP_PASSWORD', '')
AUTH_LDAP_USER_SEARCH = LDAPSearch(get_secret('LDAP_BASE_DN', ''), ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")

AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn"}
AUTH_LDAP_ALWAYS_UPDATE_USER = False  # Only populate fields on the first login

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'core.User'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]},
        'django.db.backends': {"level": "DEBUG", "handlers": ["console"]},
    },
}


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/London'

USE_I18N = False

USE_L10N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Login customization
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'

# Standard datetime format
DATE_FORMAT = 'j M Y'  # Used for standard formatting (e.g. {{ start_date | date }}
SHORT_DATE_FORMAT = 'j M Y'  # Used for datatables, or using {{ start_date | date:"SHORT_DATE_FORMAT" }}
DATETIME_FORMAT = 'j M Y H:i'
SHORT_DATETIME_FORMAT = 'j M Y H:i'
TIME_FORMAT = 'G:i'  # 24 hour time without leading zeroes
DATE_INPUT_FORMATS = [
    '%d %b %Y',  # '25 Oct 2006' - default in forms
    '%d %b, %Y',  # '25 Oct, 2006'
    '%Y-%m-%d',  # '2006-10-25'
    '%d/%m/%Y',  # '25/10/2006'
    '%d/%m/%y',  # '25/10/06'
    '%b %d %Y',  # 'Oct 25 2006'
    '%b %d, %Y',  # 'Oct 25, 2006'
    '%B %d %Y',  # 'October 25 2006'
    '%B %d, %Y',  # 'October 25, 2006'
    '%d %B %Y',  # '25 October 2006'
    '%d %B, %Y',  # '25 October, 2006'
]


# Email settings
EMAIL_HOST = get_secret('EMAIL_HOST', '')
DEFAULT_FROM_EMAIL = get_secret('DEFAULT_FROM_EMAIL', '')

# Celery task queue - TODO: get this using the same settings as the cache
redis_host = get_secret('REDIS_HOST', 'redis')  # Maps to redis host.
redis_port = get_secret('REDIS_PORT', 6379)  # Maps to redis port.
redis_password = get_secret('REDIS_PASSWORD', '')
CELERY_BROKER_URL = f"redis://:{redis_password}@{redis_host}:{redis_port}/1"

CELERY_RESULT_BACKEND = 'django-db'

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Since we have USE_TZ = False, celery beats must also be set to be timezone-naive
DJANGO_CELERY_BEAT_TZ_AWARE = False

# Legacy redpot url for cross-app mapping
W2P_REDPOT_URL = get_secret('W2P_REDPOT_URL', 'https://redpot-staging.conted.ox.ac.uk')
# Website url for outbound linking
PUBLIC_WEBSITE_URL = get_secret('PUBLIC_WEBSITE_URL', 'https://conted.ox.ac.uk')

# These may be unnecessary if passed into coverage from command line
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
# TEST_OUTPUT_DIR = BASE_DIR
TEST_OUTPUT_FILE_NAME = 'test_results.xml'

# WPM Credentials
WPM_FTP = get_secret(
    'WPM_FTP',
    {
        'HOST': '',
        'USER': '',
        'PASSWORD': '',
        'DIRECTORY': '',
    },
)
