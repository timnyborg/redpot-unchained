# Generated by Django 3.2.7 on 2021-09-21 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0012_auto_20210921_0959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phone',
            name='type',
            field=models.IntegerField(choices=[(None, ' –– Choose one –– '), (100, 'Phone'), (110, 'Alternative phone!'), (120, 'Mobile'), (130, 'Fax'), (200, 'Email'), (299, 'Invalid')], default=100),
        ),
    ]
