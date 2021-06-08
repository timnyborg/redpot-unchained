from dal import autocomplete

from django.forms import ModelForm, widgets

from apps.module.models import Module

from .models import Tutor, TutorModule


class ReadOnlyModelWidget(widgets.Widget):
    def __init__(self, model, *args, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        instance = self.model.objects.get(pk=value)
        # -static for b2, -plaintext for bs4.  todo: consider how to move that into the form rendering
        return f"""
            <input type="hidden" name="{name}" value="{value}">
            <div class='form-control-static form-control-plaintext'>{instance}</div>
        """


class TutorModuleEditForm(ModelForm):
    class Meta:
        model = TutorModule
        fields = [
            'role',
            'is_published',
            'is_teaching',
            'director_of_studies',
            'biography',
        ]


class TutorModuleCreateForm(ModelForm):
    class Meta:
        model = TutorModule
        fields = [
            'module',
            'tutor',
            'role',
            'is_published',
            'is_teaching',
            'director_of_studies',
            'biography',
        ]
        widgets = {
            'module': autocomplete.ModelSelect2(
                url='autocomplete:module',
                attrs={'data-minimum-input-length': 3},
            ),
            'tutor': autocomplete.ModelSelect2(
                url='autocomplete:tutor',
                attrs={'data-minimum-input-length': 3},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lock fields with initial values
        module = kwargs['initial'].get('module')
        tutor = kwargs['initial'].get('tutor')
        if module:
            self.fields['module'].widget = ReadOnlyModelWidget(Module)
        if tutor:
            self.fields['tutor'].widget = ReadOnlyModelWidget(Tutor)
