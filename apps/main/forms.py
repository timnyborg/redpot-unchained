from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.detail import DetailView


class PageTitleMixin:
    """
        View mixin which can automatically generate a title and subtitle for use in the template - both head and body.
        By default:
            Title = str(model.__name__)
            Subtitle is derived from the view's class (e.g. UpdateView => Edit)
            subtitle_object is derived from the object's canonical name (e.g. Programme(6) => Short Courses...)

        All can be overridden by setting variables, or overriding the methods
    """
    title = None
    subtitle = None
    subtitle_object = True

    def get_title(self):
        if self.title:
            return self.title
        if hasattr(self, 'model'):
            # Automatically get model name for model views
            return self.model._meta.verbose_name.capitalize()

    def get_subtitle(self):
        if self.subtitle:
            stem = self.subtitle
        elif isinstance(self, UpdateView):
            stem = 'Edit'
        elif isinstance(self, CreateView):
            stem = 'New'
        elif isinstance(self, DetailView):
            stem = 'View'
        else:
            return ''

        if hasattr(self, 'object'):
            return f'{stem} - {self.object}'
        return stem

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update({
            'title': self.get_title(),
            'subtitle': self.get_subtitle(),
        })
        return kwargs