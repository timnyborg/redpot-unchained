from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'division.yaml')
    call_command('loaddata', 'enrolment_status.yaml')
    call_command('loaddata', 'enrolment_result.yaml')
    call_command('loaddata', 'fee_type.yaml')
    call_command('loaddata', 'module_status.yaml')
    call_command('loaddata', 'portfolio.yaml')
    call_command('loaddata', 'qualification.yaml')
    call_command('loaddata', 'transaction_type.yaml')
    call_command('loaddata', 'tutor_fee_type.yaml')
    call_command('loaddata', 'tutor_fee_status.yaml')


class Migration(migrations.Migration):

    dependencies = [
        # Update this to track the last migration as baseline fixtures are added or modified
        ('core', '0001_initial'),
        ('programme', '0001_initial'),
        ('tutor_payment', '0001_initial'),
        ('enrolment', '0001_initial'),
        ('fee', '0001_initial'),
        ('invoice', '0001_initial'),
    ]

    operations = [migrations.RunPython(load_fixture)]
