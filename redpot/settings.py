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
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Sentry integration
sentry_sdk.init(
    dsn=env("SENTRY_DSN", default=None),
    integrations=[DjangoIntegration()],
    environment=env("SENTRY_ENVIRONMENT", default='dev' if DEBUG else 'unknown'),
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
]

PROJECT_APPS = [
    'apps.core',
    'apps.amendment',
    'apps.application',
    'apps.banner',
    'apps.booking',
    'apps.cabs_booking',
    'apps.contract',
    'apps.discount',
    'apps.enrolment',
    'apps.fee',
    'apps.feedback',
    'apps.finance',
    'apps.hesa',
    'apps.invoice',
    'apps.marketing',
    'apps.module',
    'apps.moodle',
    'apps.programme',
    'apps.proposal',
    'apps.qualification_aim',
    'apps.reminder',
    'apps.student',
    'apps.task_progress',
    'apps.transcript',
    'apps.tutor',
    'apps.tutor_payment',
    'apps.user',
    'apps.staff_list',
    'apps.staff_forms',
    'apps.waitlist',
    'apps.website_account',
    'apps.website_basket',
]

THIRD_PARTY_APPS = [
    'ckeditor',  # django-ckeditor
    'ckeditor_uploader',
    'fontawesomefree',
    'hijack',  # django-hijack
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

INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS + THIRD_PARTY_APPS  # Third party apps last to allow template overriding

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
    'hijack.middleware.HijackUserMiddleware',
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
                'redpot.context_processors.template_settings',
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

AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn", "role": "description"}
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
            "level": env("LDAP_LOGGING_LEVEL", default="ERROR"),
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

STATIC_ROOT: Path = BASE_DIR / 'static'
MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT: Path = env.path('MEDIA_ROOT', default=BASE_DIR / 'media')

# separate storage and URL for public website media, with sftp credentials
WEBSITE_MEDIA_SFTP_HOST = env('WEBSITE_MEDIA_SFTP_HOST', default='')
WEBSITE_MEDIA_SFTP_PARAMS = env.dict('WEBSITE_MEDIA_SFTP_PARAMS', default={})
WEBSITE_MEDIA_SFTP_ROOT: Path = env.path('WEBSITE_MEDIA_SFTP_ROOT', default=MEDIA_ROOT)
WEBSITE_MEDIA_URL = env('WEBSITE_MEDIA_URL', default=MEDIA_URL)

# separate path and URL for media only accessible via an X-Accel-Redirect header
PROTECTED_MEDIA_URL = env('PROTECTED_MEDIA_URL', default='/protected-media/')
PROTECTED_MEDIA_ROOT: Path = env.path('PROTECTED_MEDIA_ROOT', default=BASE_DIR / 'protected_media')

# URL for accessing application attachments managed by a separate app, with its own auth
APPLICATION_ATTACHMENT_URL = env('APPLICATION_ATTACHMENT_URL', default='')

# URL for accessing the admin section of the course proposal app
COURSE_PROPOSAL_ADMIN_URL = env('COURSE_PROPOSAL_ADMIN_URL', default='')

# URL for accessing the documentation/user guide, while it's hosted as a separate project
REDPOT_DOCS_URL = env('REDPOT_DOCS_URL', default='/docs/')

# URL for accessing legacy jsonrpc API
RP_API_URL = env('RP_API_URL', default='')

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
# custom email settings
SUPPORT_EMAIL = env('SUPPORT_EMAIL', default='redpot-support@conted.ox.ac.uk', validate=validate.Email())
PERSONNEL_EMAIL = env('PERSONNEL_EMAIL', 'personnel@conted.ox.ac.uk', validate=validate.Email())

# custom url settings
ANALYTICS_URL = env('ANALYTICS_URL', default=None, validate=validate.URL())
SENTRY_URL = env(
    'SENTRY_URL',
    default='https://sentry.io/organizations/university-of-oxford-conted/projects/redpot-unchained/',
    validate=validate.URL(schemes=['https']),
)
# hostname used in automated emails sent by celery tasks
CANONICAL_URL = env('CANONICAL_URL', default='https://redpot-unchained.conted.ox.ac.uk', validate=validate.URL())
SQUARE_URL = env(
    'SQUARE_URL',
    default='https://square.conted.ox.ac.uk/reports',
    validate=validate.URL(schemes=['https']),
)
PUBLIC_APPS_URL = env(
    'PUBLIC_APPS_URL', default='https://apps.conted.ox.ac.uk', validate=validate.URL(schemes=['https'])
)

# Celery task queue - TODO: get this using the same settings as the cache
redis_host = env('REDIS_HOST', default='redis')
redis_port = env.int('REDIS_PORT', default=6379)
redis_password = env('REDIS_PASSWORD', default=None)
password_component = f':{redis_password}@' if redis_password else ''  # Only add the password to the url if using AUTH
CELERY_BROKER_URL = f"redis://{password_component}{redis_host}:{redis_port}/1"

CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXPIRES = env.int('CELERY_RESULT_EXPIRES', default=3600 * 24 * 365)  # Keep a year of results by default

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Since we have USE_TZ = False, celery beats must also be set to be timezone-naive
DJANGO_CELERY_BEAT_TZ_AWARE = False

# Website url for outbound linking
PUBLIC_WEBSITE_URL = env('PUBLIC_WEBSITE_URL', default='https://conted.ox.ac.uk', validate=validate.URL())

# Base URL for the CABS api
CABS_API_URL = env(
    'CABS_API_URL',
    default='https://cabsplus.conted.ox.ac.uk/CABSServices',
    validate=validate.URL(schemes=['https']),
)
CABS_API_CREDENTIALS = env.dict('CABS_API_CREDENTIALS', default={'Username': '', 'Password': '', 'Source': ''})

# These may be unnecessary if passed into coverage from command line
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_FILE_NAME = 'test_results.xml'

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
                'audio[*]',
                'video[*]',
                'source[*]',
                'iframe[*]',
                'span(fas,far,fad,fal,fab,fa,fa-*)[!class]',
            ]
        ),
        'width': '100%',
        'removeDialogTabs': 'image:advanced;link:advanced',
        'contentsCss': [
            # css to replicate website styling
            'https://code.cdn.mozilla.net/fonts/fira.css',
            'https://use.fontawesome.com/releases/v5.7.2/css/all.css',
            PUBLIC_WEBSITE_URL + '/static/vendor/bootstrap/css/bootstrap.min.css',
            CANONICAL_URL + STATIC_URL + 'css/ckeditor.css',  # absolute to avoid relative to baseHref
        ],
        'baseHref': WEBSITE_MEDIA_URL,
        'filebrowserBrowseUrl': '',  # no browse button
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
        'width': '100%',
    },
}
CKEDITOR_STORAGE_BACKEND = 'redpot.storage_backends.WebsiteStorage'
CKEDITOR_FORCE_JPEG_COMPRESSION = True
CKEDITOR_IMAGE_BACKEND = 'redpot.ckeditor_backends.ResizingPillowBackend'
CKEDITOR_UPLOAD_PATH = 'uploads/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'
DJANGO_TABLES2_TEMPLATE = 'utility/bootstrap5_table.html'

HIJACK_INSERT_BEFORE = None  # Disable built-in popup

# Contract configuration - todo: consider moving into a settings table once we have one, consider a file:// url fetcher
CONTRACT_SIGNATORY = env('CONTRACT_SIGNATORY', default='')
CONTRACT_SIGNATURE_IMAGE = env('CONTRACT_SIGNATURE_IMAGE', default='')  # a path within the media folder
CONTRACT_SIGNATURE_EMAILS = env.list('CONTRACT_SIGNATURE_EMAILS', default=[PERSONNEL_EMAIL])

# background watermark for non-production instances
WATERMARK = env('WATERMARK', default='')

# a message to display below the topnav on every page.
# Likely only useful during the transition away from legacy, when non-devs are using test and prod environments
WARNING_BANNER = env('WARNING_BANNER', default='')

# Tag manager config
GOOGLE_TAG_MANAGER_ID = env('GOOGLE_TAG_MANAGER_ID', default='')

# Require authentication for all DRF apis
REST_FRAMEWORK = {'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated']}
