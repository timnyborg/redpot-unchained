# Generated by Django 3.2.12 on 2022-02-03 12:30

import apps.module.models
from django.db import migrations
import imagekit.models.fields
import redpot.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0015_auto_20220127_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, storage=redpot.storage_backends.WebsiteStorage(), upload_to=apps.module.models.image_filename),
        ),
    ]