# Generated by Django 3.0.14 on 2021-05-06 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fee', '0002_auto_20210506_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accommodation',
            name='type',
            field=models.IntegerField(choices=[(None, ' - Select - '), (100, 'Single'), (200, 'Twin')]),
        ),
    ]
