# Generated by Django 3.0.14 on 2021-05-06 10:39

import apps.core.utils.models
import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, null=True)),
                ('author', models.TextField(blank=True, null=True)),
                ('type', models.CharField(max_length=24)),
                ('additional_information', models.TextField(blank=True, null=True)),
                ('solo_link', models.TextField(blank=True, null=True)),
                ('isbn_shelfmark', models.TextField(blank=True, db_column='ISBN_shelfmark', null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=4, max_digits=19, null=True)),
                ('library_note', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'book',
            },
        ),
        migrations.CreateModel(
            name='BookStatus',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('status', models.TextField()),
            ],
            options={
                'db_table': 'book_status',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('address', models.CharField(max_length=128)),
                ('city', models.CharField(blank=True, max_length=64, null=True)),
                ('postcode', models.CharField(blank=True, max_length=50, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('building', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'location',
            },
        ),
        migrations.CreateModel(
            name='MarketingType',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'marketing_type',
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                (
                    'code',
                    apps.core.utils.models.UpperCaseCharField(
                        help_text='For details on codes, see <link>',
                        max_length=12,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                '^[A-Z]\\d{2}[A-Z]\\d{3}[A-Z]\\w[A-Z]$', message='Must be in the form A12B345CDE'
                            )
                        ],
                    ),
                ),
                ('title', models.CharField(max_length=80)),
                ('url', models.SlugField(blank=True, max_length=256, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('michaelmas_end', models.DateField(blank=True, null=True)),
                ('hilary_start', models.DateField(blank=True, null=True)),
                ('max_size', models.IntegerField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, max_length=512, null=True, upload_to='uploads/%Y/%m/%d/')),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('publish_date', models.DateField(blank=True, null=True)),
                ('open_date', models.DateField(blank=True, null=True)),
                ('closed_date', models.DateTimeField(blank=True, null=True)),
                ('unpublish_date', models.DateField(blank=True, null=True)),
                ('single_places', models.IntegerField(blank=True, null=True)),
                ('twin_places', models.IntegerField(blank=True, null=True)),
                ('double_places', models.IntegerField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('meeting_time', models.CharField(blank=True, max_length=32, null=True)),
                ('duration', models.FloatField(blank=True, null=True)),
                ('no_meetings', models.IntegerField(blank=True, null=True)),
                ('auto_publish', models.BooleanField(default=False)),
                ('is_published', models.BooleanField(default=False)),
                ('email', models.CharField(blank=True, max_length=256, null=True)),
                ('phone', models.CharField(blank=True, max_length=256, null=True)),
                ('source_module_code', models.CharField(blank=True, max_length=12, null=True)),
                ('overview', models.TextField(blank=True, null=True)),
                ('accommodation', models.TextField(blank=True, null=True)),
                ('how_to_apply', models.TextField(blank=True, db_column='application', null=True)),
                ('assessment_methods', models.TextField(blank=True, null=True)),
                ('certification', models.TextField(blank=True, null=True)),
                ('course_aims', models.TextField(blank=True, null=True)),
                ('level_and_demands', models.TextField(blank=True, null=True)),
                ('libraries', models.TextField(blank=True, null=True)),
                ('payment', models.TextField(blank=True, null=True)),
                ('programme_details', models.TextField(blank=True, null=True)),
                ('recommended_reading', models.TextField(blank=True, null=True)),
                ('scholarships', models.TextField(blank=True, null=True)),
                ('snippet', models.CharField(blank=True, max_length=512, null=True)),
                ('teaching_methods', models.TextField(blank=True, null=True)),
                ('teaching_outcomes', models.TextField(blank=True, null=True)),
                ('selection_criteria', models.TextField(blank=True, null=True)),
                ('it_requirements', models.TextField(blank=True, null=True)),
                ('credit_points', models.IntegerField(blank=True, null=True)),
                ('points_level', models.IntegerField(blank=True, null=True)),
                ('enrol_online', models.BooleanField(blank=True, null=True)),
                ('non_credit_bearing', models.BooleanField(default=True)),
                ('auto_feedback', models.BooleanField(default=True)),
                ('auto_reminder', models.BooleanField(default=True)),
                ('no_search', models.BooleanField(default=False)),
                ('week_number', models.IntegerField(blank=True, null=True)),
                ('custom_fee', models.CharField(blank=True, max_length=1012, null=True)),
                ('is_cancelled', models.BooleanField(default=False)),
                ('default_non_credit', models.BooleanField(blank=True, null=True)),
                ('note', models.CharField(blank=True, max_length=512, null=True)),
                ('terms_and_conditions', models.IntegerField(default=1)),
                ('apply_url', models.CharField(blank=True, max_length=512, null=True)),
                ('further_details', models.TextField(blank=True, null=True)),
                ('is_repeat', models.BooleanField(default=False)),
                ('reminder_sent_on', models.DateTimeField(blank=True, null=True)),
                ('room', models.CharField(blank=True, max_length=12, null=True)),
                ('room_setup', models.CharField(blank=True, max_length=12, null=True)),
                ('mailing_list', models.CharField(blank=True, max_length=25, null=True)),
                ('notification', models.CharField(blank=True, max_length=512, null=True)),
                ('cost_centre', models.CharField(blank=True, max_length=6, null=True)),
                (
                    'activity_code',
                    models.CharField(
                        blank=True,
                        help_text='e.g. 00',
                        max_length=2,
                        null=True,
                        validators=[django.core.validators.RegexValidator('^\\d{2}$', message='Invalid code')],
                    ),
                ),
                (
                    'source_of_funds',
                    models.CharField(
                        blank=True,
                        help_text='e.g. XA100',
                        max_length=5,
                        null=True,
                        validators=[django.core.validators.RegexValidator('^\\w{5}$', message='Invalid code')],
                    ),
                ),
                ('fee_code', models.CharField(blank=True, max_length=1, null=True)),
                ('half_term', models.DateField(blank=True, null=True)),
                ('reading_list_url', models.TextField(blank=True, null=True)),
                ('reading_list_links', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'module',
            },
        ),
        migrations.CreateModel(
            name='ModuleFormat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'module_format',
            },
        ),
        migrations.CreateModel(
            name='ModuleStatus',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=64, null=True)),
                ('publish', models.BooleanField(blank=True, null=True)),
                ('short_desc', models.CharField(blank=True, max_length=50, null=True)),
                ('waiting_list', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'module_status',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=64, null=True)),
                ('area', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'subject',
            },
        ),
        migrations.CreateModel(
            name='ModuleWaitlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listed_on', models.DateTimeField(default=datetime.datetime.now)),
                ('emailed_on', models.DateTimeField(blank=True, null=True)),
                (
                    'module',
                    models.ForeignKey(
                        db_column='module',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='waitlist',
                        to='module.Module',
                    ),
                ),
                (
                    'student',
                    models.ForeignKey(
                        db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, to='student.Student'
                    ),
                ),
            ],
            options={
                'db_table': 'module_waitlist',
            },
        ),
        migrations.CreateModel(
            name='ModuleSubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'module',
                    models.ForeignKey(
                        db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, to='module.Module'
                    ),
                ),
                (
                    'subject',
                    models.ForeignKey(
                        db_column='subject', on_delete=django.db.models.deletion.DO_NOTHING, to='module.Subject'
                    ),
                ),
            ],
            options={
                'db_table': 'module_subject',
            },
        ),
        migrations.CreateModel(
            name='ModuleMarketingType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'marketing_type',
                    models.ForeignKey(
                        db_column='marketing_type',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to='module.MarketingType',
                    ),
                ),
                (
                    'module',
                    models.ForeignKey(
                        db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, to='module.Module'
                    ),
                ),
            ],
            options={
                'db_table': 'module_marketing_type',
            },
        ),
    ]
