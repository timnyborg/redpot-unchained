from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'enrolment_status.yaml', verbosity=2)
    call_command('loaddata', 'enrolment_result.yaml', verbosity=2)


class Migration(migrations.Migration):

    dependencies = [
        ('enrolment', '0004_auto_20210211_1416'),
    ]

    operations = [
        migrations.RunPython(load_fixture)
    ]
