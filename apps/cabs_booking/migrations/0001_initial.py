# Generated by Django 3.2.12 on 2022-04-02 15:02

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('module', '0018_update_book_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='CABSBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True)),
                ('mbr_id', models.CharField(max_length=16)),
                ('confirmed', models.IntegerField(null=True)),
                ('provisional', models.IntegerField(null=True)),
                ('module', models.ForeignKey(db_column='module', on_delete=django.db.models.deletion.CASCADE, related_name='cabs_bookings', related_query_name='cabs_booking', to='module.module')),
            ],
            options={
                'db_table': 'module_cabs_booking',
            },
        ),
    ]
