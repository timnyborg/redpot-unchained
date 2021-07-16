# Generated by Django 3.2.5 on 2021-07-08 14:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='division',
            field=models.ForeignKey(db_column='division', default=1, on_delete=django.db.models.deletion.CASCADE, to='core.division'),
        ),
        migrations.AlterField(
            model_name='division',
            name='manager',
            field=models.ForeignKey(blank=True, db_column='manager', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='manager_of', to=settings.AUTH_USER_MODEL),
        ),
    ]