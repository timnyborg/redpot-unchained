import io
import zipfile
from datetime import datetime

from lxml import etree

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from apps.core.utils.views import PageTitleMixin

from . import forms, services

METHOD_MAP = {
    forms.BrochureTypes.PROSPECTUS: services.prospectus,
    forms.BrochureTypes.SUBJECT_AREA_BROCHURES: services.subject_area_brochures,
    forms.BrochureTypes.NEWSPAPER: services.newspaper,
}


class ExportXML(LoginRequiredMixin, PageTitleMixin, generic.FormView):
    form_class = forms.ExportXMLForm
    template_name = 'core/form.html'
    title = 'Marketing'
    subtitle = 'Export print publicity'

    def form_valid(self, form) -> http.HttpResponse:
        # Get the selected XML generator
        brochure_type = form.cleaned_data['brochure_type']
        xml_method = METHOD_MAP[brochure_type]
        doc_generator = xml_method(start_from=form.cleaned_data['starting_from'])

        # Add each generated file to a Zip
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'a') as zip_file:
            for filename, doc in doc_generator:
                with zip_file.open(filename, 'w') as xml_file:
                    xml_file.write(etree.tostring(doc, pretty_print=True, encoding='utf-8'))

        # Return the zip
        filename = f'{brochure_type} {datetime.now():%Y-%m-%d_%H%M}.zip'
        return http.HttpResponse(
            buffer.getvalue(),
            content_type='application/zip',
            headers={'Content-Disposition': f'inline;filename={filename}'},
        )
