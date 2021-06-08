# Generated by Django 3.0.14 on 2021-06-08 20:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programme', '0004_auto_20210523_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programmemodule',
            name='programme',
            field=models.ForeignKey(db_column='programme', limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='programme_modules', to='programme.Programme'),
        ),
    ]
