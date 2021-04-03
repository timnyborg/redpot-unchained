# Generated by Django 3.0.11 on 2021-02-04 16:34

from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'tutor_fee_type.yaml', verbosity=2)
    call_command('loaddata', 'tutor_fee_status.yaml', verbosity=2)


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_payment', '0002_auto_20210304_1244'),
    ]

    operations = [migrations.RunPython(load_fixture)]
