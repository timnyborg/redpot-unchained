# Generated by Django 3.2.8 on 2021-10-28 19:47

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='enrolment',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='hash_id',
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=40, unique=True),
        ),
    ]