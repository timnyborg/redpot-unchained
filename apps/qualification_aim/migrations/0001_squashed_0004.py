# Generated by Django 3.0.14 on 2021-06-28 09:35

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('qualification_aim', '0001_initial'), ('qualification_aim', '0002_certhemarks'), ('qualification_aim', '0003_auto_20210623_1644'), ('qualification_aim', '0004_auto_20210626_2334')]

    initial = True

    dependencies = [
        ('programme', '0007_auto_20210623_1644'),
        ('programme', '0006_auto_20210614_1652'),
        ('hesa', '0002_2021_changes'),
        ('student', '0003_auto_20210513_0812'),
        ('hesa', '0003_auto_20210626_2334'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntryQualification',
            fields=[
                ('id', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=128)),
                ('custom_description', models.CharField(blank=True, max_length=128, null=True)),
                ('elq_rank', models.IntegerField()),
                ('web_publish', models.BooleanField(db_column='web_publish')),
                ('display_order', models.IntegerField()),
            ],
            options={
                'db_table': 'entry_qualification',
                'ordering': ('display_order', 'elq_rank'),
            },
        ),
        migrations.CreateModel(
            name='ReasonForEnding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('description', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'reason_for_ending',
            },
        ),
        migrations.CreateModel(
            name='QualificationAim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('title', models.CharField(max_length=96)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('entry_qualification', models.ForeignKey(blank=True, db_column='entry_qualification', limit_choices_to=models.Q(('web_publish', True), ('id__in', ['X00', 'X06']), _connector='OR'), null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='qualification_aim.EntryQualification')),
                ('programme', models.ForeignKey(db_column='programme', limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='qualification_aims', to='programme.Programme')),
                ('student', models.ForeignKey(db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, to='student.Student')),
                ('study_location', models.ForeignKey(db_column='study_location', limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='programme.StudyLocation', null=True, blank=True)),
                ('sits_code', models.CharField(blank=True, help_text="Maps to SITS' enrolment code", max_length=12, null=True, verbose_name='SITS code')),
                ('reason_for_ending', models.ForeignKey(blank=True, db_column='reason_for_ending', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='qualification_aim.ReasonForEnding')),
            ],
            options={
                'verbose_name': 'Qualification aim',
                'db_table': 'qa',
            },
        ),
        migrations.CreateModel(
            name='CertHEMarks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('courses_transferred_in', models.TextField(blank=True, null=True)),
                ('credits_transferred_in', models.IntegerField(blank=True, null=True)),
                ('assignment1_date', models.DateField(blank=True, null=True, verbose_name='Assignment 1 date')),
                ('assignment1_grade', models.IntegerField(blank=True, null=True, verbose_name='Assignment 1 grade')),
                ('assignment2_date', models.DateField(blank=True, null=True, verbose_name='Assignment 2 date')),
                ('assignment2_grade', models.IntegerField(blank=True, null=True, verbose_name='Assignment 2 grade')),
                ('assignment3_date', models.DateField(blank=True, null=True, verbose_name='Assignment 3 date')),
                ('assignment3_grade', models.IntegerField(blank=True, null=True, verbose_name='Assignment 3 grade')),
                ('journal1_date', models.DateField(blank=True, null=True, verbose_name='Journal 1 date')),
                ('journal2_date', models.DateField(blank=True, null=True, verbose_name='Journal 2 date')),
                ('journal_cats_points', models.IntegerField(blank=True, null=True, verbose_name='Journal CATS points')),
                ('is_introductory_course', models.BooleanField(default=False, verbose_name='Introductory course')),
                ('qualification_aim', models.OneToOneField(db_column='qa', on_delete=django.db.models.deletion.DO_NOTHING, related_name='certhe_marks', to='qualification_aim.QualificationAim')),
                ('subject', models.ForeignKey(blank=True, db_column='subject', limit_choices_to={'id__in': {100046: 'Creative writing', 100299: 'Archaeology', 100302: 'History', 100306: 'Art history', 100337: 'Philosophy', 100601: 'Political economy', 100782: 'Architectural history', 101037: 'Literature'}}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='hesa.HECoSSubject')),
            ],
            options={
                'db_table': 'certhe_marks',
                'verbose_name': 'Certificate of Higher Education marks',
            },
        ),
    ]
