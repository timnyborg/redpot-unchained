# Generated by Django 3.2.4 on 2021-07-01 17:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0003_auto_20210701_1503'),
    ]

    operations = [
        migrations.CreateModel(
            name='RightToWorkDocumentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rtw_type', models.IntegerField(choices=[(1, 'List A (permanent)'), (2, 'List B (limited)'), (3, 'Started pre-1997'), (4, 'Working overseas - RTW not required')], db_column='rtw_type')),
                ('name', models.CharField(max_length=64)),
                ('display_order', models.IntegerField(default=0)),
                ('limited_hours', models.BooleanField()),
            ],
            options={
                'db_table': 'rtw_document_type',
            },
        ),
        migrations.AddField(
            model_name='tutor',
            name='rtw_type',
            field=models.IntegerField(blank=True, choices=[(1, 'List A (permanent)'), (2, 'List B (limited)'), (3, 'Started pre-1997'), (4, 'Working overseas - RTW not required')], db_column='rtw_type', null=True, verbose_name='List'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='rtw_check_by',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Check done by'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='rtw_check_on',
            field=models.DateField(blank=True, null=True, verbose_name='Date check done'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='rtw_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Document valid until'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='rtw_start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Document issued on'),
        ),
        migrations.AddField(
            model_name='tutor',
            name='rtw_document_type',
            field=models.ForeignKey(blank=True, db_column='rtw_document_type', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='tutor.righttoworkdocumenttype', verbose_name='Document type'),
        ),
    ]
