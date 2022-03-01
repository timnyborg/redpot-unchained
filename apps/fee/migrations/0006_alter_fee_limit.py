# Generated by Django 3.2.7 on 2021-10-05 16:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_auto_20211005_1651'),
        ('fee', '0005_auto_20211005_1303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fee',
            name='limit',
            field=models.ForeignKey(blank=True, db_column='limit', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fees', related_query_name='fee', to='booking.limit'),
        ),
    ]
