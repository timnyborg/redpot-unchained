# Generated by Django 3.0.14 on 2021-05-13 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('programme', '0002_auto_20210513_0856'),
        ('module', '0002_auto_20210506_1039'),
    ]

    operations = [
        migrations.CreateModel(
            name='HECoSSubject',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('definition', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'hecos_subject',
            },
        ),
        migrations.CreateModel(
            name='HESACostCentre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=64, null=True)),
                ('price_group', models.CharField(blank=True, max_length=2, null=True)),
            ],
            options={
                'db_table': 'hesa_cost_centre',
            },
        ),
        migrations.CreateModel(
            name='ProgrammeHecosSubject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.IntegerField()),
                ('hecos_subject', models.ForeignKey(db_column='hecos_subject', on_delete=django.db.models.deletion.DO_NOTHING, to='hesa.HECoSSubject')),
                ('programme', models.ForeignKey(db_column='programme', on_delete=django.db.models.deletion.DO_NOTHING, to='programme.Programme')),
            ],
            options={
                'db_table': 'programme_hecos_subject',
            },
        ),
        migrations.CreateModel(
            name='ModuleHECoSSubject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_by', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('percentage', models.IntegerField()),
                ('hecos_subject', models.ForeignKey(db_column='hecos_subject', on_delete=django.db.models.deletion.DO_NOTHING, to='hesa.HECoSSubject')),
                ('module', models.ForeignKey(db_column='module', on_delete=django.db.models.deletion.DO_NOTHING, to='module.Module')),
            ],
            options={
                'db_table': 'module_hecos_subject',
            },
        ),
        migrations.AddField(
            model_name='hecossubject',
            name='cost_centre',
            field=models.ForeignKey(blank=True, db_column='cost_centre', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='hesa.HESACostCentre'),
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('academic_year', models.IntegerField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(blank=True, max_length=32, null=True)),
                ('filename', models.CharField(blank=True, max_length=512, null=True)),
            ],
            options={
                'db_table': 'hesa_batch',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('programme', models.IntegerField(blank=True, null=True)),
                ('ukprn_fk', models.IntegerField(db_column='UKPRN_FK', default=10007774)),
                ('courseid', models.CharField(blank=True, db_column='COURSEID', max_length=8, null=True)),
                ('owncourseid', models.IntegerField(blank=True, db_column='OWNCOURSEID', null=True)),
                ('reducedc', models.CharField(db_column='REDUCEDC', default='00', max_length=2)),
                ('courseaim', models.CharField(blank=True, db_column='COURSEAIM', max_length=3, null=True)),
                ('ctitle', models.CharField(blank=True, db_column='CTITLE', max_length=128, null=True)),
                ('ttcid', models.IntegerField(db_column='TTCID', default=0)),
                ('collorg', models.CharField(db_column='COLLORG', default='0000', max_length=4)),
                ('clsdcrs', models.IntegerField(db_column='CLSDCRS', default=0)),
                ('msfund', models.CharField(blank=True, db_column='MSFUND', max_length=2, null=True)),
                ('awardbod', models.IntegerField(db_column='AWARDBOD', default=10007774)),
                ('batch', models.ForeignKey(blank=True, db_column='batch', null=True,
                                            on_delete=django.db.models.deletion.DO_NOTHING, to='hesa.Batch')),
            ],
            options={
                'db_table': 'hesa_course',
                'unique_together': {('batch', 'courseid')},
            },
        ),
        migrations.CreateModel(
            name='StudentOnModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolment', models.IntegerField(blank=True, null=True)),
                ('instanceid_fk', models.CharField(blank=True, db_column='INSTANCEID_FK', max_length=16, null=True)),
                ('modid', models.CharField(blank=True, db_column='MODID', max_length=16, null=True)),
                ('modstat', models.IntegerField(db_column='MODSTAT', default=2)),
                ('modout', models.CharField(blank=True, db_column='MODOUT', max_length=3, null=True)),
                ('batch', models.ForeignKey(db_column='batch', on_delete=django.db.models.deletion.DO_NOTHING,
                                            to='hesa.Batch')),
            ],
            options={
                'db_table': 'hesa_student_on_module',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student', models.IntegerField()),
                ('ukprn_fk', models.IntegerField(db_column='UKPRN_FK', default=10007774)),
                ('husid', models.CharField(blank=True, db_column='HUSID', max_length=32, null=True)),
                ('ownstu', models.IntegerField(blank=True, db_column='OWNSTU', null=True)),
                ('birthdte', models.DateField(blank=True, db_column='BIRTHDTE', null=True)),
                ('surname', models.CharField(blank=True, db_column='SURNAME', max_length=64, null=True)),
                ('fnames', models.CharField(blank=True, db_column='FNAMES', max_length=64, null=True)),
                ('sexid', models.IntegerField(blank=True, db_column='SEXID', null=True)),
                ('nation', models.CharField(blank=True, db_column='NATION', max_length=2, null=True)),
                ('ethnic', models.IntegerField(blank=True, db_column='ETHNIC', null=True)),
                ('disable', models.CharField(blank=True, db_column='DISABLE', max_length=2, null=True)),
                ('ttaccom', models.IntegerField(blank=True, db_column='TTACCOM', null=True)),
                ('ttpcode', models.CharField(blank=True, db_column='TTPCODE', max_length=32, null=True)),
                ('ssn', models.CharField(blank=True, db_column='SSN', max_length=32, null=True)),
                ('scn', models.IntegerField(blank=True, db_column='SCN', null=True)),
                ('relblf', models.CharField(blank=True, db_column='RELBLF', max_length=2, null=True)),
                ('batch', models.ForeignKey(db_column='batch', on_delete=django.db.models.deletion.DO_NOTHING,
                                            to='hesa.Batch')),
            ],
            options={
                'db_table': 'hesa_student',
            },
        ),
        migrations.CreateModel(
            name='QualificationsAwarded',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instanceid_fk', models.CharField(blank=True, db_column='INSTANCEID_FK', max_length=16, null=True)),
                ('qual', models.CharField(blank=True, db_column='QUAL', max_length=3, null=True)),
                ('batch', models.ForeignKey(db_column='batch', on_delete=django.db.models.deletion.DO_NOTHING,
                                            to='hesa.Batch')),
            ],
            options={
                'db_table': 'hesa_qualifications_awarded',
            },
        ),
        migrations.CreateModel(
            name='ModuleSubject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modid_fk', models.CharField(db_column='MODID_FK', max_length=32)),
                ('costcn', models.IntegerField(blank=True, db_column='COSTCN', null=True)),
                ('modsbjp', models.IntegerField(db_column='MODSBJP')),
                ('modsbj', models.CharField(db_column='MODSBJ', max_length=6)),
                ('batch', models.ForeignKey(db_column='batch', on_delete=django.db.models.deletion.DO_NOTHING,
                                            to='hesa.Batch')),
            ],
            options={
                'db_table': 'hesa_module_subject',
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.IntegerField(blank=True, null=True)),
                ('ukprn_fk', models.IntegerField(db_column='UKPRN_FK', default=10007774)),
                ('modid', models.CharField(blank=True, db_column='MODID', max_length=32, null=True)),
                ('mtitle', models.CharField(blank=True, db_column='MTITLE', max_length=80, null=True)),
                ('fte', models.DecimalField(blank=True, db_column='FTE', decimal_places=2, max_digits=10, null=True)),
                ('pcolab', models.IntegerField(db_column='PCOLAB', default=0)),
                ('crdtscm', models.IntegerField(db_column='CRDTSCM', default=1)),
                ('crdtpts', models.CharField(blank=True, db_column='CRDTPTS', max_length=3, null=True)),
                ('levlpts', models.IntegerField(blank=True, db_column='LEVLPTS', null=True)),
                ('tinst', models.IntegerField(blank=True, db_column='TINST', null=True)),
                ('batch', models.ForeignKey(db_column='batch', on_delete=django.db.models.deletion.DO_NOTHING,
                                            to='hesa.Batch')),
            ],
            options={
                'db_table': 'hesa_module',
            },
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instapp', models.IntegerField(db_column='INSTAPP', default=0)),
                ('recid', models.IntegerField(db_column='RECID')),
                ('ukprn', models.IntegerField(db_column='UKPRN', default=10007774)),
                ('batch', models.ForeignKey(db_column='batch', on_delete=django.db.models.deletion.DO_NOTHING,
                                            to='hesa.Batch')),
            ],
            options={
                'db_table': 'hesa_institution',
            },
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qa', models.IntegerField(blank=True, null=True)),
                ('instanceid', models.CharField(blank=True, db_column='INSTANCEID', max_length=16, null=True)),
                ('ownstu_fk', models.IntegerField(blank=True, db_column='OWNSTU_FK', null=True)),
                ('numhus', models.CharField(blank=True, db_column='NUMHUS', max_length=16, null=True)),
                ('reducedi', models.CharField(db_column='REDUCEDI', default='00', max_length=2)),
                ('campid', models.CharField(db_column='CAMPID', default='A', max_length=1)),
                ('comdate', models.DateField(blank=True, db_column='COMDATE', null=True)),
                ('mode', models.IntegerField(blank=True, db_column='MODE', null=True)),
                ('stuload', models.IntegerField(blank=True, db_column='STULOAD', null=True)),
                ('splength', models.IntegerField(blank=True, db_column='SPLENGTH', null=True)),
                ('unitlgth', models.IntegerField(db_column='UNITLGTH', default=9)),
                ('enddate', models.DateField(blank=True, db_column='ENDDATE', null=True)),
                ('rsnend', models.CharField(blank=True, db_column='RSNEND', max_length=2, null=True)),
                ('feeelig', models.IntegerField(blank=True, db_column='FEEELIG', null=True)),
                ('specfee', models.IntegerField(db_column='SPECFEE', default=9)),
                ('mstufee', models.CharField(blank=True, db_column='MSTUFEE', max_length=2, null=True)),
                ('fundlev', models.IntegerField(blank=True, db_column='FUNDLEV', null=True)),
                ('fundcode', models.IntegerField(blank=True, db_column='FUNDCODE', null=True)),
                ('yearstu', models.IntegerField(db_column='YEARSTU', default=1)),
                ('yearprg', models.IntegerField(db_column='YEARPRG', default=99)),
                ('fundcomp', models.IntegerField(blank=True, db_column='FUNDCOMP', null=True)),
                ('typeyr', models.IntegerField(blank=True, db_column='TYPEYR', null=True)),
                ('locsdy', models.CharField(blank=True, db_column='LOCSDY', max_length=1, null=True)),
                ('exchange', models.CharField(db_column='EXCHANGE', default='N', max_length=1)),
                ('disall', models.IntegerField(blank=True, db_column='DISALL', null=True)),
                ('festumk', models.IntegerField(db_column='FESTUMK', default=2)),
                ('grossfee', models.IntegerField(blank=True, db_column='GROSSFEE', null=True)),
                ('feeregime', models.IntegerField(blank=True, db_column='FEEREGIME', default=20, null=True)),
                ('netfee', models.IntegerField(blank=True, db_column='NETFEE', null=True)),
                ('bridge', models.IntegerField(db_column='BRIDGE', default=0)),
                ('elq', models.CharField(blank=True, db_column='ELQ', max_length=2, null=True)),
                ('rcstdnt', models.IntegerField(blank=True, db_column='RCSTDNT', null=True)),
                ('mcdate', models.DateField(blank=True, db_column='MCDATE', null=True)),
                ('batch', models.ForeignKey(db_column='batch', on_delete=django.db.models.deletion.DO_NOTHING,
                                            to='hesa.Batch')),
                ('courseid', models.CharField(db_column='COURSEID', max_length=8)),
            ],
            options={
                'db_table': 'hesa_instance',
            },
        ),
        migrations.CreateModel(
            name='EntryProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instanceid_fk', models.CharField(blank=True, db_column='INSTANCEID_FK', max_length=16, null=True)),
                ('domicile', models.CharField(blank=True, db_column='DOMICILE', max_length=2, null=True)),
                ('qualent3', models.CharField(blank=True, db_column='QUALENT3', max_length=3, null=True)),
                ('postcode', models.CharField(blank=True, db_column='POSTCODE', max_length=32, null=True)),
                ('careleaver', models.IntegerField(blank=True, db_column='CARELEAVER', default=99, null=True)),
                ('batch', models.ForeignKey(db_column='batch', on_delete=django.db.models.deletion.DO_NOTHING,
                                            to='hesa.Batch')),
            ],
            options={
                'db_table': 'hesa_entry_profile',
            },
        ),
        migrations.CreateModel(
            name='CourseSubject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courseid_fk', models.CharField(blank=True, db_column='COURSEID_FK', max_length=8, null=True)),
                ('sbjca', models.CharField(blank=True, db_column='SBJCA', max_length=6, null=True)),
                ('sbjpcnt', models.IntegerField(blank=True, db_column='SBJPCNT', null=True)),
                ('batch', models.ForeignKey(db_column='batch', on_delete=django.db.models.deletion.DO_NOTHING,
                                            to='hesa.Batch')),
            ],
            options={
                'db_table': 'hesa_course_subject',
            },
        ),
    ]