# Generated by Django 3.0.14 on 2021-05-06 10:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('invoice', '0002_auto_20210506_1039'),
        ('programme', '0001_initial'),
        ('module', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='division',
            field=models.ForeignKey(
                db_column='division',
                default=1,
                limit_choices_to=models.Q(('id__gt', 8), ('id__lt', 5), _connector='OR'),
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='programme.Division',
            ),
        ),
        migrations.AddField(
            model_name='module',
            name='format',
            field=models.ForeignKey(
                blank=True,
                db_column='format',
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='module.ModuleFormat',
            ),
        ),
        migrations.AddField(
            model_name='module',
            name='location',
            field=models.ForeignKey(
                blank=True,
                db_column='location',
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='module.Location',
            ),
        ),
        migrations.AddField(
            model_name='module',
            name='marketing_types',
            field=models.ManyToManyField(through='module.ModuleMarketingType', to='module.MarketingType'),
        ),
        migrations.AddField(
            model_name='module',
            name='payment_plans',
            field=models.ManyToManyField(through='invoice.ModulePaymentPlan', to='invoice.PaymentPlanType'),
        ),
        migrations.AddField(
            model_name='module',
            name='portfolio',
            field=models.ForeignKey(
                db_column='portfolio',
                default=1,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='programme.Portfolio',
            ),
        ),
        migrations.AddField(
            model_name='module',
            name='status',
            field=models.ForeignKey(
                db_column='status',
                default=10,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to='module.ModuleStatus',
            ),
        ),
        migrations.AddField(
            model_name='module',
            name='subjects',
            field=models.ManyToManyField(through='module.ModuleSubject', to='module.Subject'),
        ),
        migrations.AddField(
            model_name='book',
            name='module',
            field=models.ForeignKey(
                db_column='module',
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='books',
                to='module.Module',
            ),
        ),
        migrations.AddField(
            model_name='book',
            name='status',
            field=models.ForeignKey(
                db_column='status', on_delete=django.db.models.deletion.DO_NOTHING, to='module.BookStatus'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='modulesubject',
            unique_together={('module', 'subject')},
        ),
        migrations.AlterUniqueTogether(
            name='modulemarketingtype',
            unique_together={('module', 'marketing_type')},
        ),
    ]
