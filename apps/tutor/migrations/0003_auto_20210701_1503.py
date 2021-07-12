# Generated by Django 3.2.4 on 2021-07-01 15:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0002_help_text'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tutor',
            options={'permissions': [('edit_bank_details', "Can view and edit a tutor's banking details")]},
        ),
        migrations.AlterField(
            model_name='tutor',
            name='accountname',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Account name'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='accountno',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Account #'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='appointment_id',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Appointment ID'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='bankname',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Bank name'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='branchaddress',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Branch address'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='employee_no',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Employee #'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='iban',
            field=models.CharField(blank=True, help_text='Enter without spaces', max_length=34, null=True, validators=[django.core.validators.RegexValidator('^[A-z]{2}\\d{2}[A-z\\d]{4}\\d{7,20}$', 'Must be in the form AB12CDEF3456789')], verbose_name='IBAN'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='nino',
            field=models.CharField(blank=True, help_text='Enter without spaces', max_length=64, null=True, verbose_name='National insurance #'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='other_bank_details',
            field=models.CharField(blank=True, help_text='E.g. routing numbers', max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='sortcode',
            field=models.CharField(blank=True, max_length=8, null=True, validators=[django.core.validators.RegexValidator('(\\d{6}|\\d\\d-\\d\\d-\\d\\d)', 'Must be in the form 12-34-56 or 123456')], verbose_name='Sort code'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='swift',
            field=models.CharField(blank=True, help_text='Enter without spaces', max_length=11, null=True, validators=[django.core.validators.RegexValidator('^[A-z]{6}[A-z\\d]{2,5}$', 'Must be in the form ABCDEF12')], verbose_name='SWIFT'),
        ),
    ]
