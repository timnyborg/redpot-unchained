"""Allows CI/CD to check for missing migrations without needing a database connection:
   python manage.py makemigrations --check --dry-run --settings redpot.migration_check_settings
"""

# Import needed for INSTALLED_APPS, etc.
from redpot.settings import *  # noqa: F401 F403

DATABASES = {'default': {'ENGINE': 'django.db.backends.dummy'}}
