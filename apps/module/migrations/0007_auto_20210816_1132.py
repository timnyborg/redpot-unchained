# Generated by Django 3.2.6 on 2021-08-16 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hesa', '0004_alter_modulehecossubject_percentage'),
        ('module', '0006_alter_subject_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='hecos_subjects',
            field=models.ManyToManyField(through='hesa.ModuleHECoSSubject', to='hesa.HECoSSubject'),
        ),
        migrations.AlterField(
            model_name='module',
            name='marketing_types',
            field=models.ManyToManyField(help_text='These decide how the course is displayed in the website search results, and in print material', through='module.ModuleMarketingType', to='module.MarketingType', blank=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='subjects',
            field=models.ManyToManyField(help_text='These decide how the course is displayed in the website search results, and in print material', through='module.ModuleSubject', to='module.Subject', verbose_name='Subjects (marketing)', blank=True),
        ),
    ]
