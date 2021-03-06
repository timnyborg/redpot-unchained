# Generated by Django 3.2.9 on 2021-11-09 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0017_auto_20211001_2004'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='student',
            options={'permissions': [('merge_student', 'Merge student records')], 'verbose_name': 'Person'},
        ),
        migrations.RemoveField(
            model_name='studentarchive',
            name='husid',
        ),
        migrations.AlterField(
            model_name='studentarchive',
            name='json',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='studentarchive',
            name='source',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='studentarchive',
            name='target',
            field=models.IntegerField(),
        ),
    ]
