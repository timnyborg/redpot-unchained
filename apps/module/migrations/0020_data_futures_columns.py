# Generated by Django 3.2.13 on 2022-04-28 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0019_alter_module_cost_centre'),
    ]

    operations = [
        migrations.AddField(
            model_name='pointslevel',
            name='data_futures_code',
            field=models.IntegerField(default=99),
            preserve_default=False,
        ),
    ]
