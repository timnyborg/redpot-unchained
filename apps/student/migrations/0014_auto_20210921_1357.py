# Generated by Django 3.2.7 on 2021-09-21 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0013_alter_phone_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otherid',
            name='type',
            field=models.IntegerField(choices=[(1, 'Student Bar code ID'), (2, 'Passport ID'), (3, 'Visa ID'), (4, 'HESA ID'), (5, 'Regulatory Body Ref. Number (eg. GMC)'), (6, 'Unique Learner Number (ULN)'), (7, 'SSO username'), (8, 'OSS person number'), (9, 'Student support number'), (10, 'Alumni number')]),
        ),
        migrations.DeleteModel(
            name='OtherIdType',
        ),
    ]
