# Generated by Django 3.0.11 on 2021-03-01 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactiontype',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
