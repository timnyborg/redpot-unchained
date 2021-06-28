# Generated by Django 3.0.14 on 2021-06-28 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('student', '0005_auto_20210623_1644'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('username', models.EmailField(error_messages={'unique': 'This username is already in use'}, help_text='This must be a valid email address', max_length=256, unique=True)),
                ('password', models.CharField(blank=True, help_text='This is an encrypted value, not the actual password', max_length=256)),
                ('is_disabled', models.BooleanField(default=False, verbose_name='Disabled?')),
                ('reset_password_key', models.CharField(blank=True, editable=False, max_length=512, null=True)),
                ('student', models.ForeignKey(db_column='student', on_delete=django.db.models.deletion.DO_NOTHING, related_name='website_accounts', related_query_name='website_account', to='student.Student')),
            ],
            options={
                'db_table': 'login',
                'permissions': [('edit_password', 'Can edit website account passwords')],
            },
        ),
    ]
