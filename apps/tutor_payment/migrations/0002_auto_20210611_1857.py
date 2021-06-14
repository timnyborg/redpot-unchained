# Generated by Django 3.0.14 on 2021-06-11 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tutorfee',
            options={'permissions': [('raise', 'Can raise tutor payments'), ('approve', 'Can approve tutor payments'), ('transfer', 'Can transfer tutor payments to central finance')]},
        ),
        migrations.AlterField(
            model_name='tutorfee',
            name='batch',
            field=models.PositiveIntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='tutorfee',
            name='details',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
