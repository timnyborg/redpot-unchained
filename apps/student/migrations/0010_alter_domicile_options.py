# Generated by Django 3.2.7 on 2021-09-01 20:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0009_address_labels'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='domicile',
            options={'ordering': ('sort_order', 'name')},
        ),
    ]