from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from . import models


class List(LoginRequiredMixin, generic.ListView):
    queryset = models.Banner.objects.past()
    paginate_by = 20
    template_name = 'banner/list.html'
    extra_context = {'title': 'Updates'}
