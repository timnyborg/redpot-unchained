# Generated by Django 3.0.14 on 2021-05-06 10:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('module', '0001_initial'),
        ('application', '0001_initial'),
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseapplication',
            name='module',
            field=models.ForeignKey(
                db_column='module',
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='applications',
                related_query_name='application',
                to='module.Module',
            ),
        ),
        migrations.AddField(
            model_name='courseapplication',
            name='student',
            field=models.ForeignKey(
                db_column='student',
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='applications',
                related_query_name='application',
                to='student.Student',
            ),
        ),
    ]
