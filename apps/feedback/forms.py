from dal import autocomplete

from django import forms

from apps.module import models


class CommentAndReportForm(forms.Form):
    def __init__(self, tutors_choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tutors'].choices = tutors_choices

    comments = forms.CharField(label='Admin/Director comments', max_length=1000, widget=forms.Textarea)
    tutors = forms.MultipleChoiceField(
        label='Send PDF report to the following tutors:',
        choices=(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )


class PreviewQuestionnaireForm(forms.Form):
    submit_label = 'Next'
    module_code = forms.ModelChoiceField(
        models.Module.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='autocomplete:module',
            attrs={'data-minimum-input-length': 3, 'class': 'basicAutoComplete'},
        ),
        label='Module Code (or) Module Title',
    )


class FeedbackRequestForm(forms.Form):
    submit_label = 'Next'
    module_code = forms.ModelChoiceField(
        models.Module.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='autocomplete:module',
            attrs={'data-minimum-input-length': 3, 'class': 'basicAutoComplete'},
        ),
        label='Module Code (or) Module Title',
    )
