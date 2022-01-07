# Generated by Django 3.0.14 on 2021-05-06 10:39

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('husid', models.BigIntegerField(blank=True, null=True, verbose_name='HUSID')),
                ('surname', models.CharField(max_length=40)),
                ('firstname', models.CharField(max_length=40)),
                ('title', models.CharField(blank=True, max_length=20, null=True)),
                ('middlename', models.CharField(blank=True, max_length=40, null=True)),
                ('nickname', models.CharField(blank=True, max_length=64, null=True)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=1, null=True)),
                ('domicile', models.IntegerField()),
                ('nationality', models.IntegerField()),
                ('ethnicity', models.IntegerField()),
                ('religion_or_belief', models.IntegerField(default=99)),
                ('disability', models.IntegerField(blank=True, null=True)),
                ('occupation', models.CharField(blank=True, max_length=128, null=True)),
                ('termtime_postcode', models.CharField(blank=True, max_length=32, null=True)),
                ('note', models.CharField(blank=True, max_length=1024, null=True)),
                ('no_publicity', models.BooleanField(blank=True, null=True)),
                ('is_flagged', models.BooleanField(default=False)),
                ('is_eu', models.BooleanField(blank=True, null=True)),
                ('deceased', models.BooleanField(blank=True, db_column='Deceased', null=True)),
                ('disability_detail', models.CharField(blank=True, max_length=2048, null=True)),
                ('disability_action', models.CharField(blank=True, max_length=256, null=True)),
                ('dars_optout', models.BooleanField(default=True)),
                ('termtime_accommodation', models.IntegerField(blank=True, null=True)),
                ('sits_id', models.IntegerField(blank=True, null=True)),
                ('highest_qualification', models.CharField(blank=True, max_length=128, null=True)),
                ('mail_optin', models.BooleanField(default=False)),
                ('mail_optin_on', models.DateTimeField(blank=True, null=True)),
                ('mail_optin_method', models.CharField(blank=True, max_length=64, null=True)),
                ('email_optin', models.BooleanField(default=False)),
                ('email_optin_method', models.CharField(blank=True, max_length=64, null=True)),
                ('email_optin_on', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'student',
            },
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('email', models.CharField(max_length=64)),
                ('note', models.CharField(blank=True, max_length=128, null=True)),
                ('is_default', models.BooleanField(default=True)),
                (
                    'student',
                    models.ForeignKey(
                        db_column='student',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='emails',
                        related_query_name='email',
                        to='student.Student',
                    ),
                ),
            ],
            options={
                'db_table': 'email',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                (
                    'type',
                    models.IntegerField(
                        choices=[
                            (100, 'Permanent'),
                            (110, 'Home'),
                            (111, 'Next of Kin'),
                            (400, 'College'),
                            (410, 'Oxford College'),
                            (500, 'Work'),
                            (510, 'Work - Line Manager'),
                        ],
                        db_column='type',
                        default=100,
                    ),
                ),
                ('line1', models.CharField(max_length=128)),
                ('line2', models.CharField(blank=True, max_length=128, null=True)),
                ('line3', models.CharField(blank=True, max_length=128, null=True)),
                ('town', models.CharField(blank=True, max_length=64, null=True)),
                ('countystate', models.CharField(blank=True, max_length=64, null=True)),
                ('country', models.CharField(blank=True, max_length=64, null=True)),
                ('postcode', models.CharField(blank=True, max_length=32, null=True)),
                ('formatted', models.CharField(blank=True, max_length=1024, null=True)),
                ('is_default', models.BooleanField(default=True)),
                ('is_billing', models.BooleanField(default=False)),
                ('sits_type', models.CharField(blank=True, editable=False, max_length=1, null=True)),
                (
                    'student',
                    models.ForeignKey(
                        db_column='student',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='addresses',
                        related_query_name='address',
                        to='student.Student',
                    ),
                ),
            ],
            options={
                'db_table': 'address',
            },
        ),
    ]
