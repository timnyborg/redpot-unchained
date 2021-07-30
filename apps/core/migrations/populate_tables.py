from django.db import migrations
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'account.yaml')
    call_command('loaddata', 'domicile.yaml')
    call_command('loaddata', 'division.yaml')
    call_command('loaddata', 'entry_qualification.yaml')
    call_command('loaddata', 'enrolment_status.yaml')
    call_command('loaddata', 'enrolment_result.yaml')
    call_command('loaddata', 'ethnicity.yaml')
    call_command('loaddata', 'fee_type.yaml')  # depends on account
    call_command('loaddata', 'module_status.yaml')
    call_command('loaddata', 'nationality.yaml')
    call_command('loaddata', 'payment_plan_status.yaml')
    call_command('loaddata', 'payment_plan_type.yaml')
    call_command('loaddata', 'portfolio.yaml')
    call_command('loaddata', 'qualification.yaml')
    call_command('loaddata', 'study_location.yaml')
    call_command('loaddata', 'transaction_type.yaml')
    call_command('loaddata', 'tutor_fee_type.yaml')
    call_command('loaddata', 'tutor_fee_status.yaml')


class Migration(migrations.Migration):

    dependencies = [
        # Update this to track the last migration as baseline fixtures are added or modified
        ('core', '0002_auto_20210708_1429'),
        ('programme', '0002_auto_20210513_0856'),
        ('tutor_payment', '0001_initial'),
        ('enrolment', '0001_initial'),
        ('fee', '0004_feetype_account'),
        ('finance', '0001_initial'),
        ('invoice', '0001_initial'),
        ('qualification_aim', '0001_initial'),
        ('student', '0006_auto_20210722_1228'),
    ]

    operations = [migrations.RunPython(load_fixture)]
