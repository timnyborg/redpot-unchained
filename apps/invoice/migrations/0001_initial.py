# Generated by Django 3.0.11 on 2021-02-25 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('programme', '0003_auto_20210211_1416'),
        ('module', '0003_populate_module_status'),
        ('enrolment', '0004_auto_20210211_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('number', models.IntegerField(unique=True)),
                ('prefix', models.CharField(blank=True, max_length=32, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('fao', models.CharField(blank=True, max_length=128, null=True)),
                ('invoiced_to', models.CharField(blank=True, max_length=128, null=True)),
                ('line1', models.CharField(blank=True, max_length=128, null=True)),
                ('line2', models.CharField(blank=True, max_length=128, null=True)),
                ('line3', models.CharField(blank=True, max_length=128, null=True)),
                ('town', models.CharField(blank=True, max_length=64, null=True)),
                ('countystate', models.CharField(blank=True, max_length=64, null=True)),
                ('country', models.CharField(blank=True, max_length=64, null=True)),
                ('postcode', models.CharField(blank=True, max_length=32, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=4, max_digits=19, null=True)),
                ('custom_narrative', models.BooleanField()),
                ('narrative', models.TextField(blank=True, null=True)),
                ('ref_no', models.CharField(blank=True, max_length=64, null=True)),
                ('division', models.IntegerField(blank=True, null=True)),
                ('allocation', models.IntegerField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, db_column='duedate', null=True)),
                ('contact_person', models.CharField(blank=True, max_length=128, null=True)),
                ('contact_email', models.CharField(blank=True, max_length=255, null=True)),
                ('contact_phone', models.CharField(blank=True, max_length=64, null=True)),
                ('company', models.CharField(blank=True, max_length=128, null=True)),
                ('formatted_addressee', models.TextField(blank=True, null=True)),
                ('vat_no', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'invoice',
            },
        ),
        migrations.CreateModel(
            name='PaymentPlanType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('name', models.CharField(max_length=128)),
                ('deposit', models.DecimalField(decimal_places=2, max_digits=16)),
                ('payments', models.IntegerField(blank=True, null=True)),
                ('payments_due', models.CharField(blank=True, choices=[('IMMEDIATELY', 'Immediately'), ('TERMLY', 'Termly'), ('MONTHLY', 'Monthly')], max_length=32, null=True)),
                ('start_month', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'payment_plan_type',
            },
        ),
        migrations.CreateModel(
            name='TransactionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=32, null=True)),
                ('is_cash', models.BooleanField()),
                ('is_active', models.BooleanField()),
            ],
            options={
                'db_table': 'transaction_type',
            },
        ),
        migrations.CreateModel(
            name='ModulePaymentPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.ForeignKey(db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, to='module.Module')),
                ('plan_type', models.ForeignKey(db_column='plan_type', on_delete=django.db.models.deletion.DO_NOTHING, to='invoice.PaymentPlanType')),
            ],
            options={
                'db_table': 'module_payment_plan',
            },
        ),
        migrations.CreateModel(
            name='Ledger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('amount', models.DecimalField(decimal_places=4, max_digits=19)),
                ('finance_code', models.CharField(blank=True, max_length=64, null=True)),
                ('narrative', models.CharField(max_length=128)),
                ('allocation', models.IntegerField()),
                ('ref_no', models.IntegerField(blank=True, null=True)),
                ('batch', models.IntegerField(blank=True, null=True)),
                ('division', models.ForeignKey(blank=True, db_column='division', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='programme.Division')),
                ('enrolment', models.ForeignKey(blank=True, db_column='enrolment', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='enrolment.Enrolment')),
                ('type', models.ForeignKey(db_column='type', on_delete=django.db.models.deletion.DO_NOTHING, to='invoice.TransactionType')),
            ],
            options={
                'db_table': 'ledger',
            },
        ),
        migrations.CreateModel(
            name='InvoiceLedger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_no', models.IntegerField(blank=True, null=True)),
                ('allocation', models.ForeignKey(db_column='allocation', on_delete=django.db.models.deletion.DO_NOTHING, related_name='invoice_ledger_allocations', to='invoice.Invoice', to_field='number')),
                ('invoice', models.ForeignKey(db_column='invoice', on_delete=django.db.models.deletion.DO_NOTHING, related_name='invoice_ledger', to='invoice.Invoice')),
                ('ledger', models.ForeignKey(db_column='ledger', on_delete=django.db.models.deletion.DO_NOTHING, related_name='invoice_ledger', to='invoice.Ledger')),
            ],
            options={
                'db_table': 'invoice_ledger',
            },
        ),
        migrations.AddField(
            model_name='invoice',
            name='allocated_ledger_items',
            field=models.ManyToManyField(related_name='allocated_invoice', through='invoice.InvoiceLedger', to='invoice.Ledger'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='ledger_items',
            field=models.ManyToManyField(through='invoice.InvoiceLedger', to='invoice.Ledger'),
        ),
        migrations.CreateModel(
            name='PaymentPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('amount', models.DecimalField(decimal_places=4, max_digits=19)),
            ],
            options={
                'db_table': 'payment_plan',
            },
        ),
        migrations.CreateModel(
            name='PaymentPlanStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'payment_plan_status',
            },
        ),
        migrations.AlterField(
            model_name='invoice',
            name='custom_narrative',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='PaymentPlanSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('due_date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=16)),
                ('number', models.IntegerField()),
                ('is_deposit', models.BooleanField()),
                ('payment_plan', models.ForeignKey(db_column='payment_plan', on_delete=django.db.models.deletion.DO_NOTHING, related_name='schedule', to='invoice.PaymentPlan')),
            ],
            options={
                'db_table': 'payment_plan_schedule',
            },
        ),
        migrations.AddField(
            model_name='paymentplan',
            name='invoice',
            field=models.OneToOneField(db_column='invoice', on_delete=django.db.models.deletion.DO_NOTHING, related_name='payment_plan', to='invoice.Invoice'),
        ),
        migrations.AddField(
            model_name='paymentplan',
            name='status',
            field=models.ForeignKey(db_column='status', on_delete=django.db.models.deletion.DO_NOTHING, to='invoice.PaymentPlanStatus'),
        ),
        migrations.AddField(
            model_name='paymentplan',
            name='type',
            field=models.ForeignKey(db_column='type', on_delete=django.db.models.deletion.DO_NOTHING, to='invoice.PaymentPlanType'),
        ),
    ]
