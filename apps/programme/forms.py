from django.forms import ModelForm
from apps.main.forms import Bootstrap3FormMixin
from apps.programme.models import Programme

# Create the form class.
class ProgrammeForm(Bootstrap3FormMixin, ModelForm):
    class Meta:
        model = Programme
        fields = ['title', 'division', 'portfolio', 'qualification', 'email', 'phone', 
                  'student_load', 'funding_level', 'funding_source', 'study_mode',
                  'study_location', 'is_active', 'contact_list_display', 'sits_code'
                  ]
                  