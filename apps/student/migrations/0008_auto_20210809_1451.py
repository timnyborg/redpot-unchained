# Generated by Django 3.2.6 on 2021-08-09 14:51

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0007_auto_20210722_1328'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otheridtype',
            name='msaccess_mask',
        ),
        migrations.AlterField(
            model_name='emergencycontact',
            name='created_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='emergencycontact',
            name='created_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='emergencycontact',
            name='modified_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='emergencycontact',
            name='modified_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='emergencycontact',
            name='student',
            field=models.OneToOneField(db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, related_name='emergency_contact', to='student.student'),
        ),
        migrations.AlterField(
            model_name='enquiry',
            name='created_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='enquiry',
            name='created_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='enquiry',
            name='modified_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='enquiry',
            name='modified_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='otheridtype',
            name='description',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='phone',
            name='created_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='phone',
            name='created_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='phone',
            name='modified_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='phone',
            name='modified_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='phone',
            name='student',
            field=models.ForeignKey(db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, related_name='phones', to='student.student'),
        ),
        migrations.AlterField(
            model_name='studentarchive',
            name='created_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='studentarchive',
            name='created_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='studentarchive',
            name='modified_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='studentarchive',
            name='modified_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='suspension',
            name='created_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='suspension',
            name='created_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='suspension',
            name='modified_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='suspension',
            name='modified_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='suspension',
            name='student',
            field=models.ForeignKey(blank=True, db_column='student', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='suspensions', to='student.student'),
        ),
    ]
