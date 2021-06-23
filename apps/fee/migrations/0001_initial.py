# Generated by Django 3.0.14 on 2021-05-06 10:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('enrolment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accommodation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('type', models.IntegerField(choices=[(100, 'Single'), (200, 'Twin')])),
                ('note', models.CharField(blank=True, max_length=256, null=True)),
            ],
            options={
                'db_table': 'accommodation',
            },
        ),
        migrations.CreateModel(
            name='Catering',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'catering',
            },
        ),
        migrations.CreateModel(
            name='FeeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('narrative', models.CharField(blank=True, max_length=64, null=True)),
                ('display_order', models.IntegerField(blank=True, null=True)),
                ('is_tuition', models.BooleanField()),
                ('is_active', models.IntegerField()),
            ],
            options={
                'db_table': 'fee_type',
                'ordering': ('display_order',),
            },
        ),
        migrations.CreateModel(
            name='Limit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('description', models.CharField(max_length=128)),
                ('places', models.IntegerField()),
                ('www_buffer', models.IntegerField(default=0, help_text='Spaces that cannot be booked online')),
            ],
            options={
                'db_table': 'limit',
            },
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('amount', models.DecimalField(decimal_places=4, max_digits=19)),
                ('description', models.CharField(max_length=64)),
                ('finance_code', models.CharField(blank=True, max_length=64, null=True)),
                (
                    'eu_fee',
                    models.BooleanField(
                        db_column='eufee',
                        default=False,
                        help_text='Only payable by Home/EU students?',
                        verbose_name='Home/EU',
                    ),
                ),
                (
                    'is_visible',
                    models.BooleanField(
                        default=True, help_text='Make this fee visible on the website', verbose_name='Visible'
                    ),
                ),
                (
                    'is_payable',
                    models.BooleanField(
                        default=True, help_text='Make this fee payable on the website', verbose_name='Payable'
                    ),
                ),
                (
                    'is_catering',
                    models.BooleanField(default=False, help_text='Includes catering', verbose_name='Catering'),
                ),
                (
                    'is_single_accom',
                    models.BooleanField(
                        default=False, help_text='Includes a single accommodation', verbose_name='Single accommodation'
                    ),
                ),
                (
                    'is_twin_accom',
                    models.BooleanField(
                        default=False, help_text='Includes a double accommodation', verbose_name='Double accommodation'
                    ),
                ),
                (
                    'credit_fee',
                    models.BooleanField(default=False, help_text='Additional fee to take a weekly class for credit'),
                ),
                (
                    'end_date',
                    models.DateField(
                        blank=True, help_text='Optional: day on which to remove the fee from the website', null=True
                    ),
                ),
                ('allocation', models.IntegerField(blank=True, default=0, null=True)),
                ('catering_bookings', models.ManyToManyField(through='fee.Catering', to='enrolment.Enrolment')),
                (
                    'limit',
                    models.ForeignKey(
                        blank=True,
                        db_column='limit',
                        help_text='Todo: Manage limits link',
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name='fees',
                        related_query_name='fee',
                        to='fee.Limit',
                    ),
                ),
            ],
            options={
                'db_table': 'fee',
            },
        ),
    ]