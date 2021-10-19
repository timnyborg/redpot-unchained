from __future__ import annotations

import re
from io import BytesIO
from typing import Union

from mailmerge import MailMerge

from django import http
from django.http import HttpResponse
from django.template.exceptions import TemplateDoesNotExist
from django.views.generic.base import View
from django.views.generic.list import MultipleObjectMixin


class MailMergeView(MultipleObjectMixin, View):
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

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        self.queryset = self.get_queryset()

        filename = self.get_filename(self.queryset)
        filename = re.sub(r'[,()\']', '', filename)

        template = self.get_template_file(self.queryset)
        context = self.get_merge_data()

        try:
            with open(template, 'rb') as file:
                doc = self._merge(file, context)
        except FileNotFoundError as e:
            raise TemplateDoesNotExist(f'Template file not found: {e}')

        return HttpResponse(
            content=doc,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
        )

    def get_filename(self, queryset) -> str:
        """Sets the download filename.  Override if a dynamic filename is required."""
        return self.filename

    def get_template_file(self, queryset) -> str:
        """Which docx template to use.  Override if a dynamic template is required."""
        return self.template_file

    def _merge(self, file, context) -> bytes:
        document = MailMerge(file)
        output = BytesIO()

        if isinstance(context, (tuple, list)):
            # Multiple records & pages
            document.merge_templates(context, separator='continuous_section')
        else:
            # Single page
            document.merge(**context)

        document.write(output)

        return output.getvalue()

    def get_merge_data(self) -> Union[list[dict], dict]:
        """
        Return a list of dicts for a paginated mail merge document
        Return a single dict for a single mail merge  # todo: reconsider?

        Best if overridden
        """
        return list(self.queryset.all().values())
