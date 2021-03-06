# Generated by Django 3.2.7 on 2021-09-07 22:08

import datetime

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0011_alter_student_gender'),
    ]

    operations = [
        migrations.CreateModel(
            name='Religion',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('web_publish', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'religion_or_belief',
                'ordering': ('name',),
            },
        ),
        migrations.AlterModelOptions(
            name='disability',
            options={'ordering': ('display_order', 'description')},
        ),
        migrations.AlterModelOptions(
            name='ethnicity',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='nationality',
            options={'ordering': ('sort_order', 'name')},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'verbose_name': 'Person'},
        ),
        migrations.AlterField(
            model_name='disability',
            name='created_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='disability',
            name='created_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='disability',
            name='modified_by',
            field=models.CharField(blank=True, editable=False, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='disability',
            name='modified_on',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='domicile',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='ethnicity',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='nationality',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='student',
            name='deceased',
            field=models.BooleanField(db_column='deceased', default=False),
        ),
        migrations.AlterField(
            model_name='student',
            name='domicile',
            field=models.ForeignKey(db_column='domicile', default=181, limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='student.domicile'),
        ),
        migrations.AlterField(
            model_name='student',
            name='firstname',
            field=models.CharField(max_length=40, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='student',
            name='husid',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='HESA ID'),
        ),
        migrations.AlterField(
            model_name='student',
            name='is_eu',
            field=models.BooleanField(blank=True, null=True, verbose_name='Home/EU?'),
        ),
        migrations.AlterField(
            model_name='student',
            name='is_flagged',
            field=models.BooleanField(default=False, help_text="Put details in the 'note' field", verbose_name='Student flagged'),
        ),
        migrations.AlterField(
            model_name='student',
            name='middlename',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Middle name(s)'),
        ),
        migrations.AlterField(
            model_name='student',
            name='nationality',
            field=models.ForeignKey(db_column='nationality', default=181, limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='student.nationality'),
        ),
        migrations.AlterField(
            model_name='student',
            name='nickname',
            field=models.CharField(blank=True, help_text='If called something other than first name', max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='sits_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='SITS ID'),
        ),
        migrations.AlterField(
            model_name='student',
            name='religion_or_belief',
            field=models.ForeignKey(db_column='religion_or_belief', default=99, on_delete=django.db.models.deletion.DO_NOTHING, to='student.religion'),
        ),
    ]
