# Generated by Django 3.2.10 on 2022-01-06 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programme', '0007_auto_20210623_1644'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='programme',
            options={'ordering': ('title',), 'permissions': [('edit_restricted_fields', 'Can edit restricted programme fields (e.g. sits_id)')]},
        ),
    ]
