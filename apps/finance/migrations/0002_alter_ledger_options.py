# Generated by Django 3.2.10 on 2022-01-06 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ledger',
            options={'permissions': [('print_receipt', 'Can print receipts for payments')]},
        ),
    ]
