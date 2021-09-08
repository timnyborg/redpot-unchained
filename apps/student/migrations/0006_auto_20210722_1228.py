# Generated by Django 3.2.5 on 2021-07-22 12:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0005_auto_20210722_1228'),
        ('student', '0005_auto_20210623_1644'),
    ]

    operations = [

        migrations.CreateModel(
            name='DietType',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'diet_type',
            },
        ),
        migrations.CreateModel(
            name='Ethnicity',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
            ],
            options={
                'db_table': 'ethnicity',
            },
        ),
        migrations.CreateModel(
            name='OtherIdType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=64, null=True)),
                ('msaccess_mask', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'other_id_type',
            },
        ),
        migrations.CreateModel(
            name='PhoneType',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=32, null=True)),
            ],
            options={
                'db_table': 'phone_type',
            },
        ),
        migrations.CreateModel(
            name='StudentArchive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('husid', models.BigIntegerField(blank=True, null=True)),
                ('source', models.IntegerField(blank=True, null=True)),
                ('target', models.IntegerField(blank=True, null=True)),
                ('json', models.TextField(blank=True, null=True)),
                ('created_by', models.CharField(blank=True, max_length=32, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=32, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'student_archive',
            },
        ),
        migrations.CreateModel(
            name='Suspension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('expected_return_date', models.DateField(blank=True, null=True)),
                ('actual_return_date', models.DateField(blank=True, null=True)),
                ('reason', models.IntegerField(blank=True, null=True)),
                ('note', models.CharField(blank=True, max_length=256, null=True)),
                ('created_by', models.CharField(blank=True, max_length=16, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=16, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('student', models.ForeignKey(blank=True, db_column='student', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='student.student')),
            ],
            options={
                'db_table': 'suspension',
            },
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=64)),
                ('note', models.CharField(blank=True, max_length=128, null=True)),
                ('is_default', models.BooleanField()),
                ('created_by', models.CharField(blank=True, max_length=16, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=16, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('student', models.ForeignKey(db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, to='student.student')),
                ('type', models.ForeignKey(db_column='type', on_delete=django.db.models.deletion.DO_NOTHING, to='student.phonetype')),
            ],
            options={
                'db_table': 'phone',
            },
        ),
        migrations.CreateModel(
            name='Enquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('detail', models.TextField(blank=True, null=True)),
                ('created_by', models.CharField(blank=True, max_length=16, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=16, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('module', models.ForeignKey(db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, related_name='enquiries', to='module.module')),
                ('student', models.ForeignKey(db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, related_name='enquiries', to='student.student')),
            ],
            options={
                'db_table': 'enquiry',
            },
        ),
        migrations.CreateModel(
            name='Disability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=64, null=True)),
                ('created_by', models.CharField(blank=True, max_length=16, null=True)),
                ('created_on', models.DateTimeField(blank=True, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=16, null=True)),
                ('modified_on', models.DateTimeField(blank=True, null=True)),
                ('web_publish', models.BooleanField()),
                ('display_order', models.IntegerField(blank=True, null=True)),
                ('custom_description', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'disability',
                'unique_together': {('id', 'description', 'custom_description')},
            },
        ),
        migrations.CreateModel(
            name='Diet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(blank=True, max_length=512, null=True)),
                ('student', models.OneToOneField(db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, to='student.student')),
                ('type', models.ForeignKey(blank=True, db_column='type', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='student.diettype')),
            ],
            options={
                'db_table': 'diet',
            },
        ),
        migrations.AlterField(
            model_name='otherid',
            name='type',
            field=models.OneToOneField(db_column='type', on_delete=django.db.models.deletion.DO_NOTHING, to='student.otheridtype'),
        ),
        migrations.AlterField(
            model_name='student',
            name='disability',
            field=models.ForeignKey(db_column='disability', on_delete=django.db.models.deletion.DO_NOTHING, to='student.disability', blank=True, null= True),
        ),
        migrations.AlterField(
            model_name='student',
            name='ethnicity',
            field=models.ForeignKey(db_column='ethnicity', default=99, on_delete=django.db.models.deletion.DO_NOTHING, to='student.ethnicity'),
        ),
    ]
