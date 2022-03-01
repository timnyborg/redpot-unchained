# Generated by Django 3.0.14 on 2021-05-13 08:12

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_nexthusid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Domicile',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('is_in_eu', models.BooleanField()),
                ('hesa_code', models.CharField(max_length=8)),
                ('sort_order', models.IntegerField()),
                ('is_active', models.BooleanField()),
            ],
            options={
                'db_table': 'domicile',
            },
        ),
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('is_in_eu', models.BooleanField()),
                ('hesa_code', models.CharField(max_length=8)),
                ('sort_order', models.IntegerField()),
                ('is_active', models.BooleanField()),
            ],
            options={
                'db_table': 'nationality',
            },
        ),
        migrations.CreateModel(
            name='OtherID',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('number', models.CharField(blank=True, max_length=64, null=True)),
                ('type', models.IntegerField(choices=[(1, 'Student Card'), (7, 'Sso'), (8, 'Oss'), (9, 'Ssn')])),
                ('note', models.CharField(blank=True, max_length=64, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                (
                    'student',
                    models.ForeignKey(
                        db_column='student',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='other_ids',
                        related_query_name='other_id',
                        to='student.Student',
                    ),
                ),
            ],
            options={
                'db_table': 'other_id',
                'verbose_name': 'Other ID',
            },
        ),
        migrations.CreateModel(
            name='MoodleID',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('moodle_id', models.IntegerField(unique=True)),
                ('first_module_code', models.CharField(max_length=12)),
                (
                    'student',
                    models.OneToOneField(
                        db_column='student',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='moodle_id',
                        to='student.Student',
                    ),
                ),
            ],
            options={
                'db_table': 'moodle_id',
            },
        ),
        migrations.AlterField(
            model_name='student',
            name='domicile',
            field=models.ForeignKey(
                db_column='domicile', on_delete=django.db.models.deletion.DO_NOTHING, to='student.Domicile'# to: revert after MSSQL 1.1.1 fixed
            ),
        ),
        migrations.AlterField(
            model_name='student',
            name='nationality',
            field=models.ForeignKey(
                db_column='nationality', on_delete=django.db.models.deletion.DO_NOTHING, to='student.Nationality', default=181
            ),
        ),
    ]
