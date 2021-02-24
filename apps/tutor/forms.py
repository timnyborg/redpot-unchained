from django.forms import ModelForm

from .models import TutorModule


class TutorModuleEditForm(ModelForm):
    class Meta:
        model = TutorModule
        fields = [
            'role',
            'biography',
            'is_published',
            'is_teaching',
            'director_of_studies',
        ]
