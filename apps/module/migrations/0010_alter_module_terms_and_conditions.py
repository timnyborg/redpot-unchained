# Generated by Django 3.2.7 on 2021-09-17 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0009_auto_20210910_1244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='terms_and_conditions',
            field=models.IntegerField(blank=True, choices=[(1, 'Open access courses'), (2, 'Selective short courses')], null=True),
        ),
    ]