# Generated by Django 3.2.6 on 2021-08-20 12:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qualification_aim', '0003_auto_20210722_1228'),
        ('enrolment', '0005_auto_20210614_1738'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='enrolment',
            options={'permissions': [('edit_mark', "User can edit enrolments' marks")]},
        ),
        migrations.AlterModelOptions(
            name='enrolmentresult',
            options={'ordering': ('display_order', 'id')},
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='qa',
            field=models.ForeignKey(db_column='qa', on_delete=django.db.models.deletion.DO_NOTHING, related_name='enrolments', related_query_name='enrolment', to='qualification_aim.qualificationaim', verbose_name='Qualification aim'),
        ),
        migrations.AlterField(
            model_name='enrolment',
            name='result',
            field=models.ForeignKey(db_column='result', default='7', limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='enrolment.enrolmentresult'),
        ),
        migrations.AlterField(
            model_name='enrolmentresult',
            name='allow_certificate',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='enrolmentresult',
            name='description',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='enrolmentresult',
            name='display_order',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='enrolmentstatus',
            name='description',
            field=models.CharField(max_length=64),
        ),
    ]