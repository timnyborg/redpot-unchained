# Generated by Django 3.2.10 on 2022-01-06 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0003_alter_contract_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contract',
            options={'permissions': [('approve_contract', 'Can be assigned and approve tutor contracts'), ('cancel_contract', 'Can cancel tutor contracts'), ('sign_contract', 'Can sign tutor contracts')]},
        ),
    ]
