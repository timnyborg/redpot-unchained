from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.student.models import Student

from . import forms, models, passwords


class Create(LoginRequiredMixin, SuccessMessageMixin, AutoTimestampMixin, PageTitleMixin, generic.CreateView):
    model = models.WebsiteAccount
    form_class = forms.CreateForm
    template_name = 'core/form.html'
    success_message = 'Login %(username)s added'

    def get_subtitle(self) -> str:
        return f'New – {self.student}'

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form) -> http.HttpResponse:
        form.instance.student = self.student
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.student.get_absolute_url() + '#login'


class Edit(LoginRequiredMixin, SuccessMessageMixin, AutoTimestampMixin, PageTitleMixin, generic.UpdateView):
    # todo: recent login history (may belong elsewhere)
    model = models.WebsiteAccount
    form_class = forms.EditForm
    template_name = 'website_account/form.html'
    success_message = 'Login %(username)s updated'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # Display account history (legacy auth event table)
        return {
            **context,
            'history': self.object.get_history().order_by('-time_stamp')[:20],
        }

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        return {
            'edit_password': self.request.user.has_perm('website_account.edit_password'),
            **kwargs,
        }

    def form_valid(self, form) -> http.HttpResponse:
        new_password = form.cleaned_data.get('new_password')
        if new_password:
            form.instance.password = passwords.make_legacy_password(new_password)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.object.student.get_absolute_url() + '#login'


class Delete(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = models.WebsiteAccount
    template_name = 'core/delete_form.html'

    def get_success_url(self) -> str:
        messages.success(self.request, f'Account {self.object} deleted')
        return self.object.student.get_absolute_url()
