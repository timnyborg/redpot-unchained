# Generated by Django 3.2.5 on 2021-07-22 12:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0004_module_payment_plans'),
        ('student', '0005_auto_20210623_1644'),
        ('application', '0002_auto_20210506_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseapplication',
            name='module',
            field=models.ForeignKey(db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, related_name='applications', related_query_name='application', to='module.module'),
        ),
        migrations.AlterField(
            model_name='courseapplication',
            name='student',
            field=models.ForeignKey(db_column='student', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='applications', related_query_name='application', to='student.student'),
        ),
    ]
