from django.forms import ModelForm
from .models import Module


# Create the form class.
class ModuleForm(ModelForm):
    class Meta:
        model = Module
        exclude = ['payment_plans']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # self.fields.pop('start_date')

