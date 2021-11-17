# Generated by Django 3.2.8 on 2021-11-16 17:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0018_auto_20211109_1317'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenderIdentity',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'gender_identity',
            },
        ),
        migrations.CreateModel(
            name='ParentalEducation',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'parental_education',
            },
        ),
        migrations.CreateModel(
            name='SexualOrientation',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'sexual_orientation',
            },
        ),
        migrations.AddField(
            model_name='student',
            name='gender_identity',
            field=models.ForeignKey(db_column='gender_identity', default=99, on_delete=django.db.models.deletion.DO_NOTHING, to='student.genderidentity'),
        ),
        migrations.AddField(
            model_name='student',
            name='parental_education',
            field=models.ForeignKey(db_column='parental_education', default=8, on_delete=django.db.models.deletion.DO_NOTHING, to='student.parentaleducation'),
        ),
        migrations.AddField(
            model_name='student',
            name='sexual_orientation',
            field=models.ForeignKey(db_column='sexual_orientation', default=99, on_delete=django.db.models.deletion.DO_NOTHING, to='student.sexualorientation'),
        ),
    ]