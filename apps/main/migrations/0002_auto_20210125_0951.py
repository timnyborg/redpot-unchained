# Generated by Django 3.0.11 on 2021-01-25 09:51

import apps.main.models
from django.db import migrations, models
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AddField(
            model_name='user',
            name='created_by',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='default_approver',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format=None, keep_meta=True, null=True, quality=0, size=[1920, 1080], upload_to=''),
        ),
        migrations.AddField(
            model_name='user',
            name='modified_by',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='modified_on',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='on_facewall',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=apps.main.models.PhoneField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='room',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
