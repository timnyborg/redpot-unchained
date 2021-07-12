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

    def get_subtitle(self):
        return f'New – {self.student}'

    def dispatch(self, request, *args, **kwargs):
        self.student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.student = self.student
        return super().form_valid(form)

    def get_success_url(self):
        return self.student.get_absolute_url() + '#login'


class Edit(LoginRequiredMixin, PageTitleMixin, generic.UpdateView):
    model = models.WebsiteAccount
    form_class = forms.EditForm
    template_name = 'core/form.html'
    success_message = 'Login %(username)s updated'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {
            'edit_password': self.request.user.has_perm('website_account.edit_password'),
            **kwargs,
        }

    def form_valid(self, form):
        new_password = form.cleaned_data.get('new_password')
        if new_password:
            form.instance.password = passwords.make_legacy_password(new_password)
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.student.get_absolute_url() + '#login'


#
#     # Display login history
#     recent_logins = idb(
#         idb.public_auth_event.description.contains(login.id)
#     ).select(
#         limitby=(0, 20),
#         orderby=~idb.public_auth_event.time_stamp
#     )
#
#     return dict(login=login, login_form=login_form, new_password_form=new_password_form, recent_logins=recent_logins)
