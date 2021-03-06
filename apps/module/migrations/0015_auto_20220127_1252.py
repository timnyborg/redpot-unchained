# Generated by Django 3.2.10 on 2022-01-27 12:52

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0014_delete_waitlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('ewert_cabs_code', models.CharField(max_length=10)),
                ('rewley_cabs_code', models.CharField(max_length=10)),
                ('always_required', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'equipment',
            },
        ),
        migrations.AlterField(
            model_name='module',
            name='accommodation',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='assessment_methods',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='certification',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='course_aims',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='further_details',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='how_to_apply',
            field=models.TextField(blank=True, db_column='application', null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='it_requirements',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='level_and_demands',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='libraries',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='overview',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='payment',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='programme_details',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='recommended_reading',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='scholarships',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)], verbose_name='Funding'),
        ),
        migrations.AlterField(
            model_name='module',
            name='selection_criteria',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)], verbose_name='Entry requirements'),
        ),
        migrations.AlterField(
            model_name='module',
            name='teaching_methods',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)]),
        ),
        migrations.AlterField(
            model_name='module',
            name='teaching_outcomes',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10000)], verbose_name='Learning outcomes'),
        ),
        migrations.CreateModel(
            name='ModuleEquipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(blank=True, default=datetime.datetime.now, editable=False, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('equipment', models.ForeignKey(db_column='equipment', on_delete=django.db.models.deletion.PROTECT, to='module.equipment')),
                ('module', models.ForeignKey(db_column='module', on_delete=django.db.models.deletion.CASCADE, to='module.module')),
            ],
            options={
                'db_table': 'module_equipment',
            },
        ),
        migrations.AddField(
            model_name='module',
            name='equipment',
            field=models.ManyToManyField(through='module.ModuleEquipment', to='module.Equipment'),
        ),
    ]
