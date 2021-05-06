# Generated by Django 3.0.14 on 2021-05-06 10:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('module', '0001_initial'),
        ('programme', '0001_initial'),
        ('invoice', '0001_initial'),
        ('enrolment', '0002_auto_20210506_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='modulepaymentplan',
            name='module',
            field=models.ForeignKey(
                db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, to='module.Module'
            ),
        ),
        migrations.AddField(
            model_name='modulepaymentplan',
            name='plan_type',
            field=models.ForeignKey(
                db_column='plan_type', on_delete=django.db.models.deletion.DO_NOTHING, to='invoice.PaymentPlanType'
            ),
        ),
        migrations.AddField(
            model_name='ledger',
            name='division',
            field=models.ForeignKey(
                blank=True,
                db_column='division',
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='programme.Division',
            ),
        ),
        migrations.AddField(
            model_name='ledger',
            name='enrolment',
            field=models.ForeignKey(
                blank=True,
                db_column='enrolment',
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='enrolment.Enrolment',
            ),
        ),
        migrations.AddField(
            model_name='ledger',
            name='type',
            field=models.ForeignKey(
                db_column='type', on_delete=django.db.models.deletion.DO_NOTHING, to='invoice.TransactionType'
            ),
        ),
        migrations.AddField(
            model_name='invoiceledger',
            name='allocation',
            field=models.ForeignKey(
                db_column='allocation',
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='invoice_ledger_allocations',
                to='invoice.Invoice',
                to_field='number',
            ),
        ),
        migrations.AddField(
            model_name='invoiceledger',
            name='invoice',
            field=models.ForeignKey(
                db_column='invoice',
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='invoice_ledger',
                to='invoice.Invoice',
            ),
        ),
        migrations.AddField(
            model_name='invoiceledger',
            name='ledger',
            field=models.ForeignKey(
                db_column='ledger',
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='invoice_ledger',
                to='invoice.Ledger',
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='allocated_ledger_items',
            field=models.ManyToManyField(
                related_name='allocated_invoice', through='invoice.InvoiceLedger', to='invoice.Ledger'
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='ledger_items',
            field=models.ManyToManyField(through='invoice.InvoiceLedger', to='invoice.Ledger'),
        ),
    ]
