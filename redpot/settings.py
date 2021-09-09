"""
Django settings for redpot project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path

import environs
import ldap
import sentry_sdk
from django_auth_ldap.config import LDAPSearch
from marshmallow import validate
from sentry_sdk.integrations.django import DjangoIntegration

from django.contrib import messages
from django.core.management.utils import get_random_secret_key

# Get environment variables
env = environs.Env()
env.read_env('secrets.env')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env('SECRET_KEY', default=get_random_secret_key())
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'] if DEBUG else [])

# In production, ensure SESSION_COOKIE_SECURE = True, and enforce https at the reverse-proxy or use SECURE_SSL_REDIRECT
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)

# Sentry integration
sentry_sdk.init(
    dsn=env("SENTRY_DSN", default=None),
    integrations=[DjangoIntegration()],
    environment='dev' if DEBUG else 'prod',
    # You may wish to set the sample_rate to 1.0 in dev, but it should be scaled much lower in production
    traces_sample_rate=env.float("SENTRY_SAMPLE_RATE", default=0.01),
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
    'ckeditor',  # django-ckeditor
    'menu',  # django-simple-menu
    'django_select2',
    'django_tables2',
    'django_filters',
    'widget_tweaks',  # django-widget-tweaks
    'celery_progress',
    'django_celery_beat',
    'django_celery_results',
    'bootstrap_datepicker_plus',
    'rest_framework',
    'crispy_forms',
]

PROJECT_APPS = [
    'apps.core',
    'apps.amendment',
    'apps.application',
    'apps.discount',
    'apps.enrolment',
    'apps.fee',
    'apps.finance',
    'apps.hesa',
    'apps.invoice',
    'apps.module',
    'apps.programme',
    'apps.qualification_aim',
    'apps.student',
    'apps.tutor',
    'apps.tutor_payment',
    'apps.user',
    'apps.staff_list',
    'apps.staff_forms',
    'apps.website_account',
]

INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS

if env('REDIS_HOST', default=None):
    CACHES = {
        # To separate redis session (semi-persistent) and redis cache (ephemeral), we could define a second
        #  cache (key: session), point it to another port/instance and use it as the SESSION_CACHE_ALIAS
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": 'redis://%s:%s' % (env('REDIS_HOST'), env.int('REDIS_PORT', default=6379)),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PASSWORD": env('REDIS_PASSWORD', default=None),
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
    'redpot.middleware.IEDetectionMiddleware',
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
        'NAME': env('DB_NAME', default='redpot'),
        'ENGINE': 'mssql',
        'HOST': env('DB_HOST', default='mssql'),
        'USER': env('DB_USER', default='sa'),
        'PASSWORD': env('DB_PASSWORD', default='Test@only'),
        'TEST': {
            'NAME': env('TEST_DB_NAME', default='redpot_test'),
        },
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MESSAGE_TAGS = {
    # Overriding the error tag to match bootstrap 3
    messages.ERROR: 'danger'
}

AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",  # To enable groups & permissions
]

AUTH_LDAP_SERVER_URI = env('LDAP_HOST', default='')  # this can be a comma separated list of URIs
AUTH_LDAP_BIND_DN = env('LDAP_BIND_DN', default='')
AUTH_LDAP_BIND_PASSWORD = env('LDAP_PASSWORD', default='')
AUTH_LDAP_USER_SEARCH = LDAPSearch(env('LDAP_BASE_DN', default=''), ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")
AUTH_LDAP_START_TLS = env.bool('LDAP_START_TLS', default=True)

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
        "django_auth_ldap": {
            "level": "ERROR",
            "handlers": ["console"],
        },
        'django.db.backends': {
            "level": env("DB_LOGGING_LEVEL", default="ERROR"),
            "handlers": ["console"],
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-gb'
USE_I18N = False
USE_L10N = False

USE_TZ = False
TIME_ZONE = 'Europe/London'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [BASE_DIR / 'redpot' / 'assets']
MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = env('MEDIA_ROOT', default=BASE_DIR / 'media')

DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'PNG': ".png"}

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
    '%d %B %Y',  # '25 October 2006'
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
DATETIME_INPUT_FORMATS = [
    '%d %b %Y %H:%M',  # '25 Oct 2016 14:30' - default in forms
    '%d %B %Y %H:%M',  # '25 October 2016 14:30'
    '%d %b %Y %H:%M:%S',  # '25 Oct 2016 14:30:59'
    '%d %B %Y %H:%M:%S',  # '25 October 2016 14:30:59'
    '%Y-%m-%d %H:%M:%S',  # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M',  # '2006-10-25 14:30'
    '%d/%m/%Y %H:%M:%S',  # '25/10/2006 14:30:59'
    '%d/%m/%Y %H:%M',  # '25/10/2006 14:30'
    '%d/%m/%y %H:%M:%S',  # '25/10/06 14:30:59'
    '%d/%m/%y %H:%M',  # '25/10/06 14:30'
]
# Email settings
EMAIL_HOST = env('EMAIL_HOST', default=None)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='redpot-support@conted.ox.ac.uk', validate=validate.Email())
SUPPORT_EMAIL = env(
    'SUPPORT_EMAIL', default='redpot-support@conted.ox.ac.uk', validate=validate.Email()
)  # custom setting

# custom url settings
ANALYTICS_URL = env('ANALYTICS_URL', default=None, validate=validate.URL())
SENTRY_URL = env(
    'SENTRY_URL',
    default='https://sentry.io/organizations/university-of-oxford-conted/projects/redpot-unchained/',
    validate=validate.URL(schemes=['https']),
)
# hostname used in automated emails sent by celery tasks
CANONICAL_URL = env('CANONICAL_URL', default='https://redpot-unchained.conted.ox.ac.uk', validate=validate.URL())

# Celery task queue - TODO: get this using the same settings as the cache
redis_host = env('REDIS_HOST', default='redis')  # Maps to redis host.
redis_port = env.int('REDIS_PORT', default=6379)  # Maps to redis port.
redis_password = env('REDIS_PASSWORD', default=None)
CELERY_BROKER_URL = f"redis://:{redis_password}@{redis_host}:{redis_port}/1"

CELERY_RESULT_BACKEND = 'django-db'

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Since we have USE_TZ = False, celery beats must also be set to be timezone-naive
DJANGO_CELERY_BEAT_TZ_AWARE = False

# Legacy redpot url for cross-app mapping
W2P_REDPOT_URL = env('W2P_REDPOT_URL', default='https://redpot-staging.conted.ox.ac.uk', validate=validate.URL())
# Website url for outbound linking
PUBLIC_WEBSITE_URL = env('PUBLIC_WEBSITE_URL', default='https://conted.ox.ac.uk', validate=validate.URL())

# These may be unnecessary if passed into coverage from command line
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_FILE_NAME = 'test_results.xml'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# WPM Credentials
WPM_FTP = env.dict(
    'WPM_FTP',
    default={
        'HOST': '',
        'USER': '',
        'PASSWORD': '',
        'DIRECTORY': '',
    },
)

CKEDITOR_CONFIGS = {
    # todo: implement old config features where still required:
    #       - image upload (django-ckeditor's inbuilt handling may be preferable)
    #       - website css rules
    #       - basehref
    #       - default image alignment (config.js)
    'default': {
        'toolbar': 'custom',
        'toolbar_custom': [
            ['Format'],
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord'],
            ['Undo', 'Redo'],
            ['Scayt'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'SpecialChar'],
            ['Italic', 'Blockquote', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', 'Indent', 'Outdent'],
            ['Source'],
            ['Maximize'],
        ],
        'format_tags': 'p;h3;h4',
        'extraPlugins': 'wordcount',
        'extraAllowedContent': ';'.join(
            [
                # element[attributes]{styles}(classes)
                # See: https://ckeditor.com/docs/ckeditor4/latest/guide/dev_allowed_content_rules.html
                # Todo: triage these rules and make them stricter (esp. attributes)
                'audio[*]',
                'video[*]',
                'source[*]',
                'iframe[*]',
                'div[*](*)',
                'address[*]',
                'i[*]',
                'span[*](*)',
                'p[*](*)',
                'a[*](*)',
            ]
        ),
    },
    'links_only': {
        'toolbar': 'custom',
        'toolbar_custom': [
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord'],
            ['Undo', 'Redo'],
            ['Scayt'],
            ['Link', 'Unlink', 'Anchor'],
            ['SpecialChar'],
            ['Source'],
        ],
        'extraPlugins': 'wordcount',
    },
}
