from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'transaction_type.yaml', verbosity=2)


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_auto_20210301_1214'),
    ]

    operations = [
        migrations.RunPython(load_fixture)
    ]
