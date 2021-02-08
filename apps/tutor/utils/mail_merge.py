# Todo: put this somewhere sensible
from django.views.generic.list import MultipleObjectTemplateResponseMixin
from django.views.generic.base import View
from django.http import HttpResponse
from io import BytesIO as StringIO
import re
from mailmerge import MailMerge
from django.template.exceptions import TemplateDoesNotExist


def mail_merge(docx_file, filename, records=None, **merge_fields):
    # Can take a list of records for multiple pages: records = [{'a': 1}, {'a': 2}]
    # Or a single record, which can include repeat rows: a=1, b=2, c=3, rows=[{...}]

    document = MailMerge(docx_file)
    output = StringIO()

    if records:
        # Multiple records & pages
        document.merge_templates(records, separator='continuous_section')
    else:
        # Single page
        document.merge(**merge_fields)

    document.write(output)
    return output.getvalue()


class MailMergeView(MultipleObjectTemplateResponseMixin, View):
    """
        Can take a list of records for multiple pages:
            def get_context_data(...): 
                return [{'a': 1}, {'a': 2}]
        Or a single record, which can include repeat rows: a=1, b=2, c=3, rows=[{...}]
            def get_context_data(...):
                return {'a': 1', 'b': 2, rows: [...]}

        This could be improved by implementing an actual template engine with a loader
    """

    template_file = None
    filename = None

    def get(self, request, *args, **kwargs):
        self.queryset = self.get_queryset()

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

        filename = self.get_filename(self.queryset)

        if not filename.endswith('.docx'):
            filename += '.docx'
        filename = re.sub('[,()\']', '', filename)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

        template = self.get_template_file(self.queryset)

        context = self.get_context_data()

        try:
            with open(template, 'rb') as file:
                doc = self._merge(file, context)
                response.write(doc)
        except FileNotFoundError as e:
            raise TemplateDoesNotExist('Template file not found: %s' % e)

        return response

    def get_filename(self, queryset):
        """ Override if a dynamic filename is required. """
        return self.filename

    def get_template_file(self, queryset):
        """ Override if a dynamic template is required. """
        return self.template_file

    def _merge(self, file, context):
        document = MailMerge(file)
        output = StringIO()

        if isinstance(context, (tuple, list)):
            # Multiple records & pages
            document.merge_templates(context, separator='continuous_section')
        else:
            # Single page
            document.merge(**context)

        document.write(output)

        return output.getvalue()

    def get_context_data(self):
        """TODO: try using this on an easy model.
           Best if overridden
        """
        return list(self.queryset.all().values())
