from django.db import models
from django.db.models import Model, CharField, DateField, ForeignKey, IntegerField, BooleanField, DO_NOTHING, Q

class Module(Model):
    code = CharField(max_length=12, help_text='For details on codes, see <link>')    
    title = CharField(max_length=80)
    
    start_date = DateField(blank=True, null=True)
    end_date = DateField(blank=True, null=True)
    
    division = ForeignKey('programme.Division', DO_NOTHING, db_column='division', blank=True, null=True, limit_choices_to=Q(id__gt=8) | Q(id__lt=5))
    portfolio = ForeignKey('programme.Portfolio', DO_NOTHING, db_column='portfolio', blank=True, null=True)
    
    status = ForeignKey('ModuleStatus', DO_NOTHING, db_column='status')
    max_size = IntegerField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'module'


class ModuleStatus(Model):
    id = IntegerField(primary_key=True)
    description = CharField(max_length=64, blank=True, null=True)
    publish = BooleanField(blank=True, null=True)
    short_desc = CharField(max_length=50, blank=True, null=True)
    waiting_list = BooleanField(blank=True, null=True)   

    class Meta:
        managed = False
        db_table = 'module_status'