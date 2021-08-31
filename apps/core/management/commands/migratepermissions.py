from django.apps import apps
from django.contrib.auth.management import create_permissions
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates any missing permissions on the database for the specified apps (or all if blank)'

    def add_arguments(self, parser):
        parser.add_argument('apps', nargs='*', type=str)

    def handle(self, *args, **options):
        if options['apps']:
            app_configs = [apps.get_app_config(app) for app in options['apps']]
        else:
            app_configs = apps.get_app_configs()  # All

        for app_config in app_configs:
            app_config.models_module = True
            create_permissions(app_config, verbosity=0)
            app_config.models_module = None
