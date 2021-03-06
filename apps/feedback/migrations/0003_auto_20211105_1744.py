# Generated by Django 3.2.8 on 2021-11-05 17:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0011_auto_20211001_2003'),
        ('feedback', '0002_auto_20211028_1947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='module',
            field=models.ForeignKey(db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, to='module.module'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='your_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='feedbackadmin',
            name='module',
            field=models.ForeignKey(db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, to='module.module'),
        ),
    ]
