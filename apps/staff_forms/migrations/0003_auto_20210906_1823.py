# Generated by Django 3.2.7 on 2021-09-06 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_alter_user_image'),
        ('staff_forms', '0002_auto_20210901_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='starter',
            name='division',
            field=models.ForeignKey(db_column='division', on_delete=django.db.models.deletion.DO_NOTHING, to='core.division'),
        ),
        migrations.AlterField(
            model_name='starter',
            name='email',
            field=models.EmailField(blank=True, help_text='Required if known. If not known, you can update it later. The staff will be flagged for update.', max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='starter',
            name='lastname',
            field=models.CharField(max_length=50),
        ),
    ]