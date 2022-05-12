# Generated by Django 3.2.13 on 2022-04-21 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0023_uk_domicile_column'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='domicile',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='nationality',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='nationality',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='nationality',
            name='is_in_eu',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='nationality',
            name='sort_order',
            field=models.IntegerField(default=1),
        ),
    ]