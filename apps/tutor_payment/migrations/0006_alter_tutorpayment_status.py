# Generated by Django 3.2.7 on 2021-10-06 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_payment', '0005_rename_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorpayment',
            name='status',
            field=models.ForeignKey(db_column='status', default=1, on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='tutor_payment.paymentstatus'),
        ),
    ]
