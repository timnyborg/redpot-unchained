from datetime import datetime
from typing import Optional, Type

from import_export.resources import ModelResource

from django import http
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.views import generic
from django.views.defaults import page_not_found


class AutoTimestampMixin:
    """Automatically updates modified_by, modified_on, and created_by (if a CreateView)"""

    def form_valid(self, form):
        form.instance.modified_on = datetime.now()
        form.instance.modified_by = self.request.user.username
        if isinstance(self, generic.CreateView):
            form.instance.created_by = self.request.user.username
        return super().form_valid(form)


class PageTitleMixin:
    """
    View mixin which can automatically generate a title and subtitle for use in the template - both head and body.
    By default:
        Title = str(model.__name__)
        Subtitle is derived from the view's class (e.g. UpdateView => Edit)
        subtitle_object is derived from the object's canonical name (e.g. Programme(6) => Short Courses...)

    All can be overridden by setting variables, or overriding the methods
    """

    title: str = ""
    subtitle: str = ""
    subtitle_object: bool = True

    def get_title(self) -> str:
        if self.title:
            return self.title
        if hasattr(self, 'model') and self.model is not None:
            # Automatically get model name for model views
            return self.model._meta.verbose_name[0].upper() + self.model._meta.verbose_name[1:]
        if hasattr(self, 'queryset') and self.queryset is not None:
            # Automatically get model name for views with a queryset.  Is not None is critical, to prevent loading
            # the entire set into memory before casting as True/False!
            return self.queryset.model._meta.verbose_name[0].upper() + self.queryset.model._meta.verbose_name[1:]

    def get_subtitle(self) -> str:
        if self.subtitle:
            stem = self.subtitle
        elif isinstance(self, generic.UpdateView):
            stem = 'Edit'
        elif isinstance(self, generic.CreateView):
            stem = 'New'
        elif isinstance(self, generic.DetailView):
            stem = 'View'
        elif isinstance(self, generic.DeleteView):
            stem = 'Delete'
        else:
            return ''

        if self.subtitle_object and hasattr(self, 'object') and self.object:
            return f'{stem} – {self.object}'
        return stem

    def get_context_data(self, **kwargs) -> dict:
        kwargs = super().get_context_data(**kwargs)
        kwargs.update(
            {
                'title': self.get_title(),
                'subtitle': self.get_subtitle(),
            }
        )
        return kwargs


class DeletionFailedMessageMixin:
    """
    Causes a DeleteView to display an error message if deletion fails due to protected child records
    """

    def delete(self, request, *args, **kwargs) -> http.HttpResponse:
        try:
            self.object = self.get_object()
            self.object.delete()
        except models.ProtectedError as e:
            protected_class = e.protected_objects.pop()._meta.verbose_name
            messages.error(
                request, f"This record cannot be deleted because other records depend on it ({protected_class})"
            )
            return self.on_failure(request, *args, **kwargs)
        else:
            return self.on_success()

    def on_success(self) -> http.HttpResponse:
        """Override to add custom behaviour when the delete succeeds (e.g. a message)"""
        success_url = self.get_success_url()
        return http.HttpResponseRedirect(success_url)

    def on_failure(self, request, *args, **kwargs) -> http.HttpResponse:
        """Override to add custom behaviour when the delete fails"""
        return self.get(request, *args, **kwargs)


class ExcelExportView(generic.View):
    """A view that allows easy exporting of excel spreadsheets from django-import-export's ModelResource objects"""

    http_method_names = ['get']

    filename: str = ''
    export_class: Type[ModelResource]
    queryset: Optional[models.QuerySet] = None

    def get_filename(self) -> str:
        """Return the filename of the download"""
        if self.filename:
            return self.filename
        raise ImproperlyConfigured(
            f'{self.__class__.__name__} is missing a filename.  Define a filename, or implement get_filename()'
        )

    def get_export_class(self) -> Type[ModelResource]:
        """Return the export class to use"""
        return self.export_class

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        filename = self.get_filename()
        export_class = self.get_export_class()
        queryset = self.get_export_queryset()
        dataset = export_class().export(queryset)
        output = dataset.xlsx

        response = http.HttpResponse(
            output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def get_export_queryset(self) -> Optional[models.QuerySet]:
        """Return the queryset used in the exporter"""
        return self.queryset


def not_implemented(request: http.HttpRequest, message: str = 'Not implemented', *args, **kwargs) -> http.HttpResponse:
    """Stub view to indicate pages that haven't been implemented yet during development"""

    return page_not_found(request, exception=http.Http404(message))
