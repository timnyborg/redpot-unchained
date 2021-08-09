# Generated by Django 3.2.5 on 2021-07-22 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website_account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicAuthEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_stamp', models.DateTimeField(blank=True, null=True)),
                ('client_ip', models.CharField(blank=True, max_length=512, null=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('origin', models.CharField(blank=True, max_length=512, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'public_auth_event',
            },
        ),
    ]