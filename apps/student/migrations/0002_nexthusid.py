# Generated by Django 3.0.14 on 2021-05-06 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NextHUSID',
            fields=[
                ('year', models.IntegerField(primary_key=True, serialize=False)),
                ('next', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'next_husid',
            },
        ),
    ]
