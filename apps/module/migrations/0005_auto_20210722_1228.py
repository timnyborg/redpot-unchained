# Generated by Django 3.2.5 on 2021-07-22 12:28

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_auto_20210623_1644'),
        ('module', '0004_module_payment_plans'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ModuleWaitlist',
        ),
        migrations.CreateModel(
            name='Waitlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listed_on', models.DateTimeField(default=datetime.datetime.now)),
                ('emailed_on', models.DateTimeField(blank=True, null=True)),
                ('module', models.ForeignKey(db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, related_name='waitlists', to='module.module')),
                ('student', models.ForeignKey(db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, related_name='waitlists', to='student.student')),
            ],
            options={
                'db_table': 'module_waitlist',
            },
        )
    ]