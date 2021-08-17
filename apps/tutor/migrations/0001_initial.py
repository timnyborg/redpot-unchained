# Generated by Django 3.0.14 on 2021-05-06 10:39

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('module', '0001_initial'),
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('qualifications', models.CharField(blank=True, max_length=256, null=True)),
                ('affiliation', models.CharField(blank=True, max_length=256, null=True)),
                ('nino', models.CharField(blank=True, max_length=64, null=True)),
                ('employee_no', models.CharField(blank=True, max_length=32, null=True)),
                ('appointment_id', models.CharField(blank=True, max_length=32, null=True)),
                ('bankname', models.CharField(blank=True, max_length=64, null=True)),
                ('branchaddress', models.CharField(blank=True, max_length=128, null=True)),
                ('accountname', models.CharField(blank=True, max_length=64, null=True)),
                ('sortcode', models.CharField(blank=True, max_length=8, null=True)),
                ('accountno', models.CharField(blank=True, max_length=32, null=True)),
                ('swift', models.CharField(blank=True, max_length=11, null=True)),
                ('iban', models.CharField(blank=True, max_length=34, null=True)),
                ('other_bank_details', models.CharField(blank=True, max_length=512, null=True)),
                ('biography', models.TextField(blank=True, null=True)),
                ('image', models.CharField(blank=True, max_length=255, null=True)),
                ('rtw_check_on', models.DateField(blank=True, null=True)),
                ('rtw_check_by', models.CharField(blank=True, max_length=50, null=True)),
                ('rtw_start_date', models.DateField(blank=True, null=True)),
                ('rtw_end_date', models.DateField(blank=True, null=True)),
                ('oracle_supplier_number', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tutor',
            },
        ),
        migrations.CreateModel(
            name='TutorModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('role', models.CharField(blank=True, max_length=64)),
                ('biography', models.TextField(blank=True, null=True)),
                ('is_published', models.BooleanField(default=False)),
                ('display_order', models.IntegerField(blank=True, null=True)),
                (
                    'is_teaching',
                    models.BooleanField(
                        default=True,
                        help_text='i.e. not a course director or demonstrator',
                        verbose_name='Is this person teaching or speaking on the course?',
                    ),
                ),
                (
                    'director_of_studies',
                    models.BooleanField(
                        default=False,
                        help_text='Feedback results will be sent to director automatically',
                        verbose_name='Director of studies / course director',
                    ),
                ),
                (
                    'module',
                    models.ForeignKey(
                        db_column='module',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='tutor_modules',
                        related_query_name='tutor_module',
                        to='module.Module',
                    ),
                ),
                (
                    'tutor',
                    models.ForeignKey(
                        db_column='tutor',
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='tutor_modules',
                        related_query_name='tutor_module',
                        to='tutor.Tutor',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Tutor on module',
                'db_table': 'tutor_module',
            },
        ),
        migrations.AddField(
            model_name='tutor',
            name='modules',
            field=models.ManyToManyField(related_name='tutors', through='tutor.TutorModule', to='module.Module'),
        ),
        migrations.AddField(
            model_name='tutor',
            name='student',
            field=models.OneToOneField(
                db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, to='student.Student'
            ),
        ),
    ]
