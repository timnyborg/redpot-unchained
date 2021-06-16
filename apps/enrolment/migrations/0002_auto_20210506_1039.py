# Generated by Django 3.0.14 on 2021-05-06 10:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('module', '0001_initial'),
        ('programme', '0001_initial'),
        ('enrolment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrolment',
            name='module',
            field=models.ForeignKey(
                db_column='module',
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='enrolments',
                to='module.Module',
            ),
        ),
        migrations.AddField(
            model_name='enrolment',
            name='result',
            field=models.ForeignKey(
                db_column='result',
                default=7,
                limit_choices_to={'is_active': True},
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='enrolment.EnrolmentResult',
            ),
        ),
        migrations.AddField(
            model_name='enrolment',
            name='status',
            field=models.ForeignKey(
                db_column='status', on_delete=django.db.models.deletion.DO_NOTHING, to='enrolment.EnrolmentStatus'
            ),
        ),
    ]
