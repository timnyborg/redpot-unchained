# Generated by Django 3.0.14 on 2021-06-14 19:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualification_aim', '0001_squashed_0004'),
        ('student', '0003_auto_20210513_0812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='highest_qualification',
            field=models.ForeignKey(blank=True, db_column='highest_qualification', limit_choices_to={'is_active': True}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='qualification_aim.EntryQualification'),
        ),
    ]
