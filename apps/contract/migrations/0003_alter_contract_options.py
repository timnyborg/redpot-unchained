# Generated by Django 3.2.7 on 2021-09-29 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0002_alter_contract_tutor_module'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contract',
            options={'permissions': [('approve', 'Can be assigned and approve tutor contracts'), ('sign', 'Can sign tutor contracts')]},
        ),
    ]
