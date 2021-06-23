# Generated by Django 3.0.14 on 2021-06-14 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('student', '0003_auto_20210513_0812'),
        ('programme', '0006_auto_20210614_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntryQualification',
            fields=[
                ('id', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=128)),
                ('custom_description', models.CharField(blank=True, max_length=128, null=True)),
                ('elq_rank', models.IntegerField()),
                ('web_publish', models.BooleanField(db_column='web_publish')),
                ('display_order', models.IntegerField()),
            ],
            options={
                'db_table': 'entry_qualification',
                'ordering': ('display_order', 'elq_rank'),
            },
        ),
        migrations.CreateModel(
            name='QualificationAim',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('title', models.CharField(max_length=96)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('entry_qualification', models.ForeignKey(blank=True, db_column='entry_qualification', limit_choices_to=models.Q(('web_publish', True), ('id__in', ['X00', 'X06']), _connector='OR'), null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='qualification_aim.EntryQualification')),
                ('programme', models.ForeignKey(db_column='programme', limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='qualification_aims', to='programme.Programme')),
                ('student', models.ForeignKey(db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, to='student.Student')),
                ('study_location', models.ForeignKey(db_column='study_location', default=1, limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='programme.StudyLocation')),
            ],
            options={
                'verbose_name': 'Qualification aim',
                'db_table': 'qa',
            },
        ),
    ]