# Generated by Django 3.0.14 on 2021-05-06 10:39

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CourseApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('created_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=150, null=True)),
                ('modified_on', models.DateTimeField(default=datetime.datetime.now, editable=False, null=True, blank=True)),
                ('academic_credit', models.BooleanField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=20, null=True)),
                ('surname', models.CharField(blank=True, max_length=40, null=True)),
                ('first_name', models.CharField(blank=True, db_column='fname', max_length=40, null=True)),
                ('previous_name', models.CharField(blank=True, db_column='pname', max_length=40, null=True)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=1, null=True)),
                ('nationality', models.SmallIntegerField(blank=True, null=True)),
                ('residence', models.IntegerField(blank=True, null=True)),
                ('address1', models.CharField(blank=True, max_length=128, null=True)),
                ('address2', models.CharField(blank=True, max_length=128, null=True)),
                ('city', models.CharField(blank=True, max_length=64, null=True)),
                ('county_state', models.CharField(blank=True, max_length=64, null=True)),
                ('postcode', models.CharField(blank=True, max_length=32, null=True)),
                ('native', models.BooleanField(blank=True, null=True)),
                ('entry_qualification', models.CharField(blank=True, max_length=50, null=True)),
                ('entry_qualification_details', models.CharField(blank=True, max_length=500, null=True)),
                ('occupation', models.CharField(blank=True, max_length=128, null=True)),
                ('employer', models.CharField(blank=True, max_length=128, null=True)),
                ('statement', models.CharField(blank=True, max_length=4000, null=True)),
                ('funding', models.CharField(blank=True, max_length=250, null=True)),
                ('invoice_details', models.CharField(blank=True, max_length=200, null=True)),
                ('ethnicity', models.SmallIntegerField(blank=True, null=True)),
                ('religion', models.SmallIntegerField(blank=True, null=True)),
                ('disability', models.SmallIntegerField(blank=True, null=True)),
                ('disability_details', models.CharField(blank=True, max_length=500, null=True)),
                ('provenance', models.CharField(blank=True, max_length=32, null=True)),
                ('provenance_details', models.CharField(blank=True, max_length=128, null=True)),
                ('email_optin', models.BooleanField(blank=True, null=True)),
                ('post_optin', models.BooleanField(blank=True, null=True)),
                ('dars_optin', models.BooleanField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=64, null=True)),
                ('email', models.CharField(blank=True, max_length=64, null=True)),
                ('phone', models.CharField(blank=True, max_length=64, null=True)),
                ('test_type', models.CharField(blank=True, max_length=64, null=True)),
                ('date_taken', models.DateField(blank=True, null=True)),
                ('overall_result', models.CharField(blank=True, max_length=128, null=True)),
                ('constituent_scores', models.CharField(blank=True, max_length=128, null=True)),
                ('further_information', models.CharField(blank=True, max_length=500, null=True)),
                ('referee_name', models.CharField(blank=True, max_length=50, null=True)),
                ('referee_institution', models.CharField(blank=True, max_length=128, null=True)),
                ('referee_email_address', models.CharField(blank=True, max_length=64, null=True)),
                ('attachment_name_1', models.CharField(blank=True, max_length=50, null=True)),
                ('is_completed', models.BooleanField(blank=True, null=True)),
                ('hash', models.CharField(blank=True, max_length=64, null=True)),
                ('is_billing_same_as_postal', models.BooleanField(blank=True, null=True)),
                ('billing_address1', models.CharField(blank=True, max_length=128, null=True)),
                ('billing_address2', models.CharField(blank=True, max_length=128, null=True)),
                ('billing_city', models.CharField(blank=True, max_length=64, null=True)),
                ('billing_county_state', models.CharField(blank=True, max_length=64, null=True)),
                ('billing_postcode', models.CharField(blank=True, max_length=32, null=True)),
                ('billing_country', models.CharField(blank=True, max_length=64, null=True)),
                ('is_non_accredited', models.BooleanField(blank=True, null=True)),
                ('company_name', models.CharField(blank=True, max_length=128, null=True)),
                ('purchase_order', models.TextField(blank=True, null=True)),
                ('invoice_or_quote', models.BooleanField(blank=True, null=True)),
                ('further_details', models.CharField(blank=True, max_length=4000, null=True)),
            ],
            options={
                'db_table': 'course_application',
            },
        ),
    ]
