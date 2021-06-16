# Generated by Django 3.0.14 on 2021-05-06 10:39

import apps.core.utils.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('module', '0001_initial'),
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Programme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('title', models.CharField(max_length=96, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                (
                    'student_load',
                    models.DecimalField(
                        blank=True,
                        decimal_places=4,
                        help_text='Percent of full-time, eg. 50',
                        max_digits=10,
                        null=True,
                    ),
                ),
                (
                    'funding_level',
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (10, 'Undergraduate'),
                            (11, 'Long undergraduate'),
                            (20, 'Postgraduate taught'),
                            (21, 'Long postgraduate taught'),
                            (30, 'Postgraduate research'),
                            (31, 'Long postgraduate research'),
                            (99, 'Not in HESES population'),
                        ],
                        null=True,
                    ),
                ),
                (
                    'funding_source',
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (1, 'Office for Students'),
                            (2, 'HEFCW'),
                            (3, 'SFC'),
                            (4, 'DfE(NI)'),
                            (6, 'Welsh Government DfES (including Welsh for Adults)'),
                            (7, 'DfE'),
                            (11, 'LEA'),
                            (13, 'Welsh Government (WG)'),
                            (14, 'Scottish Government - Employability, Skills and Lifelong Learning Directorate'),
                            (21, 'Biotechnology & Biological Sciences Research Council (BBSRC)'),
                            (22, 'Medical Research Council (MRC)'),
                            (23, 'Natural Environment Research Council (NERC)'),
                            (24, 'Engineering & Physical Sciences Research Council (EPSRC)'),
                            (25, 'Economic & Social Research Council (ESRC)'),
                            (26, 'Science & Technology Facilities Council (STFC)'),
                            (27, 'Arts & Humanities Research Council (AHRC)'),
                            (29, 'Research council - not specified'),
                            (31, 'Departments of Health/NHS/Social Care'),
                            (32, 'Departments of Social Services'),
                            (34, 'Other HM government departments'),
                            (35, 'Armed forces'),
                            (37, 'Wholly NHS funded'),
                            (38, 'Partially NHS funded'),
                            (39, 'Education and Skills Funding Agency (ESFA)'),
                            (41, 'UK public corporation/nationalised industry'),
                            (42, 'UK private industry/commerce'),
                            (43, 'UK charity (medical)'),
                            (44, 'UK charity (other)'),
                            (46, 'EU commission (EC)'),
                            (51, 'Overseas government or other overseas organisation'),
                            (61, 'Own provider'),
                            (65, 'European Research Action Scheme for the Mobility of University Students (ERASMUS)'),
                            (71, 'Joint between two sources including a funding council'),
                            (72, 'Joint between two bodies excluding a funding council'),
                            (81, 'Other funding'),
                            (84, 'Multinational organisation (non-UK based)'),
                            (91, 'Funded entirely by student tuition fees'),
                        ],
                        null=True,
                    ),
                ),
                (
                    'study_mode',
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (1, 'Full-time according to Funding Council definitions.'),
                            (31, 'Part-time'),
                            (64, 'Dormant- previously part-time'),
                        ],
                        null=True,
                    ),
                ),
                ('is_active', models.BooleanField(default=True)),
                ('sits_code', models.CharField(blank=True, max_length=32, null=True)),
                ('contact_list_display', models.BooleanField(default=True)),
                ('email', models.EmailField(blank=True, max_length=64, null=True)),
                ('phone', apps.core.utils.models.PhoneField(blank=True, max_length=64, null=True)),
                (
                    'division',
                    models.ForeignKey(
                        db_column='division',
                        limit_choices_to=models.Q(('id__gt', 8), ('id__lt', 5), _connector='OR'),
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to='core.Division',
                    ),
                ),
            ],
            options={
                'db_table': 'programme',
                'permissions': [
                    (
                        'edit_registry_fields',
                        'Can edit programme fields like Study Location or Student Load (should just be one programme.edit permission',
                    ),
                    (
                        'edit_restricted_fields',
                        'Can edit dev-restricted fields (is_active, contact_list_display, sits_id',
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name='Qualification',
            fields=[
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('is_award', models.BooleanField()),
                ('is_postgraduate', models.BooleanField()),
                ('on_hesa_return', models.BooleanField()),
                ('hesa_code', models.CharField(max_length=8)),
                ('elq_rank', models.IntegerField()),
                ('is_matriculated', models.BooleanField()),
            ],
            options={
                'db_table': 'qualification',
                'ordering': ['elq_rank'],
            },
        ),
        migrations.CreateModel(
            name='StudyLocation',
            fields=[
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=64, null=True)),
                ('hesa_code', models.CharField(blank=True, max_length=8, null=True)),
                ('is_active', models.BooleanField()),
            ],
            options={
                'db_table': 'study_location',
            },
        ),
        migrations.CreateModel(
            name='ProgrammeModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'module',
                    models.ForeignKey(
                        db_column='module',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='programme_modules',
                        to='module.Module',
                    ),
                ),
                (
                    'programme',
                    models.ForeignKey(
                        db_column='programme',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='programme_modules',
                        to='programme.Programme',
                    ),
                ),
            ],
            options={
                'db_table': 'programme_module',
                'unique_together': {('programme', 'module')},
            },
        ),
        migrations.AddField(
            model_name='programme',
            name='modules',
            field=models.ManyToManyField(
                related_name='programmes', through='programme.ProgrammeModule', to='module.Module'
            ),
        ),
        migrations.AddField(
            model_name='programme',
            name='portfolio',
            field=models.ForeignKey(
                db_column='portfolio',
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='core.Portfolio',
            ),
        ),
        migrations.AddField(
            model_name='programme',
            name='qualification',
            field=models.ForeignKey(
                db_column='qualification',
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='programme.Qualification',
            ),
        ),
        migrations.AddField(
            model_name='programme',
            name='study_location',
            field=models.ForeignKey(
                blank=True,
                db_column='study_location',
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='programme.StudyLocation',
            ),
        ),
    ]
