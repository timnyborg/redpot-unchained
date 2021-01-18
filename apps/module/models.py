from django.db import models
from django.db.models import Model, CharField, DateField, ForeignKey, IntegerField, BooleanField, ImageField, DO_NOTHING, Q
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.urls import reverse


class Module(Model):
    code = CharField(max_length=12, help_text='For details on codes, see <link>')    
    title = CharField(max_length=80)
    url = models.SlugField(max_length=256, blank=True, null=True)
    
    start_date = DateField(blank=True, null=True)
    end_date = DateField(blank=True, null=True)

    michaelmas_end = DateField(blank=True, null=True)
    hilary_start = DateField(blank=True, null=True)

    division = ForeignKey('programme.Division', DO_NOTHING, db_column='division',
                          limit_choices_to=Q(id__gt=8) | Q(id__lt=5))
    portfolio = ForeignKey('programme.Portfolio', DO_NOTHING, db_column='portfolio')
    
    status = ForeignKey('ModuleStatus', DO_NOTHING, db_column='status')
    max_size = IntegerField(blank=True, null=True)

    image = ImageField(upload_to='uploads/%Y/%m/%d/', max_length=512, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[app].[module]'
        
    def __str__(self):
        return self.title

    @property
    def long_form(self):
        if self.start_date:
            return f'{self.code} - {self.title} ({self.start_date:%d %b %Y})'
        return f'{self.code} - {self.title}'

    def get_absolute_url(self):
        return reverse('module:edit', args=[self.id])

    def clean(self): 
        # Check both term start/end date fields are filled, or neither
        if bool(self.hilary_start) != bool(self.michaelmas_end):
            raise ValidationError({
                'hilary_start': 'You must provide both term dates',
                'michaelmas_end': 'You must provide both term dates',
            })

        # Check end_date is equal or later to start_date
        if self.end_date and not self.start_date:
            raise ValidationError({
                'start_date': 'Please set a start date',
            })
        elif self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': 'End date cannot be earlier than start date',
            })

        # # Check if all components that make up the finance code are supplied, or none
        # components = ['cost_centre', 'activity_code', 'source_of_funds']
        # if any(self.__attr__(field) for field in components) and not all(self.__attr__(field) for field in components):
            # for field in components:
                # if not self.__attr__(field):
                    # raise ValidationError({
                        # field: 'Please provide all of cost centre, activity code and source of funds, or neither',
                    # })
                   
        # if not all(self.__attr__(field) for field in components) and self.enrol_online:
            # raise ValidationError({
                # 'enrol_online': 'Online enrolment disallowed without cost centre, activity code and source of funds',
            # })
            
    def save(self, *args, **kwargs):
        if not self.url:
            self.url = slugify(self.title)
        # if self.status == 33: # cancelled
            # self.is_cancelled = True
            # self.auto_publish = False
        # self.update_status()  # Date changes may alter auto-status.

        super().save(*args, **kwargs)


class ModuleStatus(Model):
    id = IntegerField(primary_key=True)
    description = CharField(max_length=64, blank=True, null=True)
    publish = BooleanField(blank=True, null=True)
    short_desc = CharField(max_length=50, blank=True, null=True)
    waiting_list = BooleanField(blank=True, null=True)   

    class Meta:
        managed = False
        db_table = '[app].[module_status]'
        ordering = ['id']
        
    def __str__(self):
        return self.description