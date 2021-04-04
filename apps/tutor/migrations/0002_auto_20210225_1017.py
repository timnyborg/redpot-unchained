# Generated by Django 3.0.11 on 2021-02-25 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutormodule',
            name='director_of_studies',
            field=models.BooleanField(default=False, help_text='Feedback results will be sent to director automatically', verbose_name='Director of studies / course director'),
        ),
        migrations.AlterField(
            model_name='tutormodule',
            name='is_teaching',
            field=models.BooleanField(default=True, help_text='i.e. not a course director or demonstrator', verbose_name='Is this person teaching or speaking on the course?'),
        ),
        migrations.AlterField(
            model_name='tutormodule',
            name='role',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]