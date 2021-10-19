# Generated by Django 3.2.7 on 2021-10-05 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrolment', '0007_auto_20210929_2148'),
        ('booking', '0001_initial'),
        ('fee', '0004_feetype_account'),
    ]

    operations = [
        # move models to bookings app
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='catering',
                    name='enrolment',
                ),
                migrations.RemoveField(
                    model_name='catering',
                    name='fee',
                ),
                migrations.AlterField(
                    model_name='fee',
                    name='catering_bookings',
                    field=models.ManyToManyField(through='booking.Catering', to='enrolment.Enrolment'),
                ),
                migrations.AlterField(
                    model_name='fee',
                    name='limit',
                    field=models.ForeignKey(blank=True, db_column='limit', help_text='Todo: Manage limits link', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fees', related_query_name='fee', to='booking.limit'),
                ),
                migrations.DeleteModel(
                    name='Accommodation',
                ),
                migrations.DeleteModel(
                    name='Catering',
                ),
                migrations.DeleteModel(
                    name='Limit',
                )
            ],
            database_operations=[]
        ),
    ]