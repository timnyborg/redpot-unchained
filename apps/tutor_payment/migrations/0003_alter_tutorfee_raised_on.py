# Generated by Django 3.2.5 on 2021-07-07 18:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_payment', '0002_auto_20210611_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorfee',
            name='raised_on',
            field=models.DateTimeField(default=datetime.datetime.now, editable=False),
        ),
    ]
