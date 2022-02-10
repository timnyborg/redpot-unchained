# Generated by Django 3.2.10 on 2022-01-28 11:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.core.utils.web2py_compat


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('module', '0015_auto_20220127_1252'),
        ('tutor', '0011_alter_tutor_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProposalMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proposal', models.IntegerField()),
                ('sender', models.CharField(max_length=16)),
                ('sent_on', models.DateTimeField()),
                ('message', models.TextField()),
            ],
            options={
                'db_table': 'proposal_message',
            },
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Created'), (2, 'Tutor'), (3, 'DoS'), (4, 'Admin'), (5, 'Complete')], default=1)),
                ('title', models.CharField(max_length=80)),
                ('subjects', apps.core.utils.web2py_compat.PipeSeparatedIntegersField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('michaelmas_end', models.DateField(blank=True, null=True, verbose_name='End of first term')),
                ('hilary_start', models.DateField(blank=True, null=True, verbose_name='Start of second term')),
                ('end_date', models.DateField(blank=True, null=True)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('no_meetings', models.IntegerField(blank=True, null=True, verbose_name='# of meetings')),
                ('duration', models.FloatField(blank=True, null=True)),
                ('is_repeat', models.BooleanField(blank=True, null=True, verbose_name='Is this a repeat course?')),
                ('previous_run', models.CharField(blank=True, max_length=12, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('room_setup', models.CharField(choices=[('SEMINR', 'Seminar'), ('ECTR', 'Computer teaching'), ('BOARD', 'Boardroom'), ('CLASS', 'Classroom'), ('LECT', 'Lecture'), ('UCHRS', 'U of chairs'), ('UTBLS', 'U of tables')], default='SEMINR', max_length=12, null=True, verbose_name='Classroom layout')),
                ('max_size', models.IntegerField(blank=True, null=True, verbose_name='Class size')),
                ('reduced_size', models.IntegerField(blank=True, null=True)),
                ('reduction_reason', models.CharField(blank=True, max_length=50, null=True, verbose_name='Reason for reduction')),
                ('tutor_title', models.CharField(blank=True, max_length=16, null=True)),
                ('tutor_firstname', models.CharField(max_length=40, null=True)),
                ('tutor_nickname', models.CharField(blank=True, max_length=64, null=True)),
                ('tutor_surname', models.CharField(max_length=40, null=True)),
                ('tutor_qualifications', models.CharField(blank=True, max_length=256, null=True)),
                ('tutor_biography', models.TextField(blank=True, null=True)),
                ('field_trips', models.CharField(blank=True, max_length=60, null=True)),
                ('risk_form', models.CharField(blank=True, max_length=255, null=True, verbose_name='Risk assessment form')),
                ('snippet', models.TextField(blank=True, null=True)),
                ('overview', models.TextField(blank=True, null=True)),
                ('programme_details', models.TextField(blank=True, null=True)),
                ('course_aims', models.TextField(blank=True, null=True)),
                ('level_and_demands', models.TextField(blank=True, null=True)),
                ('assessment_methods', models.TextField(blank=True, null=True)),
                ('teaching_methods', models.TextField(blank=True, null=True)),
                ('teaching_outcomes', models.TextField(blank=True, null=True)),
                ('image', models.CharField(blank=True, max_length=255, null=True)),
                ('equipment', apps.core.utils.web2py_compat.PipeSeparatedIntegersField(blank=True, null=True, verbose_name='Required equipment')),
                ('scientific_equipment', models.CharField(blank=True, max_length=64, null=True)),
                ('additional_requirements', models.TextField(blank=True, null=True, verbose_name='Additional class requirements')),
                ('recommended_reading', models.TextField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Tutor completion due')),
                ('grammar_points', models.TextField(blank=True, null=True)),
                ('limited', models.BooleanField(default=False, help_text='Updatable fields will be limited', verbose_name='Is this a language course?')),
                ('updated_fields', apps.core.utils.web2py_compat.PipeSeparatedStringsField(blank=True, null=True)),
                ('tutor_approve', models.DateTimeField(blank=True, null=True)),
                ('dos_approve', models.DateTimeField(blank=True, null=True)),
                ('admin_approve', models.DateTimeField(blank=True, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.CharField(blank=True, max_length=16, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=16, null=True)),
                ('reminded_on', models.DateTimeField(blank=True, null=True)),
                ('dos', models.ForeignKey(blank=True, db_column='dos', null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Director of studies', to_field='username')),
                ('location', models.ForeignKey(blank=True, db_column='location', null=True, on_delete=django.db.models.deletion.PROTECT, to='module.location')),
                ('module', models.OneToOneField(db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, to='module.module')),
                ('room', models.ForeignKey(blank=True, db_column='room', null=True, on_delete=django.db.models.deletion.PROTECT, to='module.room')),
                ('tutor', models.ForeignKey(db_column='tutor', on_delete=django.db.models.deletion.PROTECT, to='tutor.tutor')),
            ],
            options={
                'verbose_name': 'Course proposal',
                'db_table': 'proposal',
                'permissions': [('approve_proposal', 'Can approve course proposals (when assigned as Director of Studies)')],
            },
        ),
    ]