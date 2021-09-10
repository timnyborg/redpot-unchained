# Generated by Django 3.2.7 on 2021-09-10 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0008_auto_20210907_1646'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointsLevel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=255)),
                ('fheq_level', models.IntegerField()),
            ],
            options={
                'db_table': 'points_level',
            },
        ),
        migrations.AlterField(
            model_name='module',
            name='points_level',
            field=models.ForeignKey(blank=True, db_column='points_level', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='module.pointslevel'),
        ),
    ]
