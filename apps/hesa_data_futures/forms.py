from datetime import datetime

from django import forms

from apps.core.utils.dates import academic_year


class CreateBatchForm(forms.Form):
    year = forms.TypedChoiceField(
        label='Academic year',
        coerce=int,
        choices=((x, x) for x in range(academic_year() + 1, 2000, -1)),
        initial=lambda: datetime.now().year - 1,
    )
