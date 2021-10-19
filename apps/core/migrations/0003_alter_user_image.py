# Generated by Django 3.2.8 on 2021-10-19 12:21

import apps.core.models
from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_user_default_approver'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to=apps.core.models.PathAndRename('images/staff_profile/')),
        ),
    ]
