# Generated by Django 3.0.14 on 2021-06-30 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0003_ledger_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='amount',
            field=models.DecimalField(decimal_places=4, editable=False, max_digits=19),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='countystate',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='County/state'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='division',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateField(db_column='duedate', null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='fao',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='FAO'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='line1',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Address line 1'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='line2',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Line 2'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='line3',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Line 3'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='number',
            field=models.IntegerField(editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='prefix',
            field=models.CharField(default='XG', editable=False, max_length=32),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='ref_no',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Customer ref. #'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='town',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='City/town'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='vat_no',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='VAT #'),
        ),
    ]