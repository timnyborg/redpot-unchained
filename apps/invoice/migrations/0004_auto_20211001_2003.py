# Generated by Django 3.2.7 on 2021-10-01 20:03

import apps.core.utils.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0003_require_contact_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='contact_email',
            field=models.EmailField(max_length=255),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='contact_phone',
            field=apps.core.utils.models.PhoneField(max_length=64),
        ),
    ]
