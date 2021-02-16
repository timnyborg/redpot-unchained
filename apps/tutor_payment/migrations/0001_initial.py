# Generated by Django 3.0.11 on 2021-02-16 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorFeeRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=64)),
                ('amount', models.DecimalField(decimal_places=4, max_digits=19)),
                ('type', models.CharField(max_length=64, null=True)),
                ('description', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'tutor_fee_rate',
            },
        ),
        migrations.CreateModel(
            name='TutorFeeStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=50, null=True)),
                ('paid', models.BooleanField()),
            ],
            options={
                'db_table': 'tutor_fee_status',
            },
        ),
        migrations.CreateModel(
            name='TutorFeeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=64, null=True)),
                ('is_hourly', models.BooleanField()),
                ('code', models.CharField(blank=True, max_length=64, null=True)),
                ('is_active', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tutor_fee_type',
            },
        ),
        migrations.CreateModel(
            name='TutorFee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=4, max_digits=19)),
                ('pay_after', models.DateField(blank=True, null=True)),
                ('details', models.CharField(blank=True, max_length=500, null=True)),
                ('batch', models.PositiveIntegerField(blank=True, null=True)),
                ('hourly_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=19, null=True)),
                ('hours_worked', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('weeks', models.IntegerField(blank=True, null=True)),
                ('approver', models.CharField(max_length=32)),
                ('raised_by', models.CharField(editable=False, max_length=50)),
                ('raised_on', models.DateTimeField(editable=False)),
                ('approved_by', models.CharField(blank=True, editable=False, max_length=50, null=True)),
                ('approved_on', models.DateTimeField(blank=True, editable=False, null=True)),
                ('transferred_by', models.CharField(blank=True, editable=False, max_length=50, null=True)),
                ('transferred_on', models.DateTimeField(blank=True, editable=False, null=True)),
                ('status', models.ForeignKey(db_column='status', on_delete=django.db.models.deletion.DO_NOTHING, to='tutor_payment.TutorFeeStatus')),
                ('tutor_module', models.ForeignKey(db_column='tutor_module', on_delete=django.db.models.deletion.DO_NOTHING, related_name='payments', related_query_name='payment', to='tutor.TutorModule')),
                ('type', models.ForeignKey(db_column='type', limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.DO_NOTHING, to='tutor_payment.TutorFeeType')),
            ],
            options={
                'db_table': 'tutor_fee',
            },
        ),
    ]
