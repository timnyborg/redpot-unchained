from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.views.generic import CreateView, FormView, TemplateView

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin

from .forms import LeaverForm, StarterForm


class SiteTitleMixin(PageTitleMixin):
    title = 'Staff Forms'


class Home(LoginRequiredMixin, SiteTitleMixin, TemplateView):
    subtitle = 'Home'
    template_name = 'staff_forms/home.html'


class StarterFormView(LoginRequiredMixin, SiteTitleMixin, AutoTimestampMixin, SuccessMessageMixin, CreateView):
    template_name = 'staff_forms/new_starter.html'
    subtitle = 'Add a new starter'
    form_class = StarterForm
    success_url = reverse_lazy('staff_forms:home')
    success_message = (
        'A new starter has been successfully added and emails have been sent to the relevant departments.'
    )

    def form_valid(self, form):
        context = {'starter': form.cleaned_data}
        subject = 'IT StaffForms - Starter'
        html_message = render_to_string('staff_forms/starter_mail_template.html', context)
        plain_message = strip_tags(html_message)
        from_email = 'personnel@conted.ox.ac.uk'
        cc_email = self.request.user.email
        cc = [cc_email]

        to = [settings.SUPPORT_EMAIL] if settings.DEBUG else []

        send_mail(subject, plain_message, from_email, to, cc, html_message=html_message)

        return super().form_valid(form)


class LeaverFormView(LoginRequiredMixin, SiteTitleMixin, SuccessMessageMixin, FormView):
    template_name = 'staff_forms/leaver.html'
    subtitle = 'Leaver details'
    form_class = LeaverForm
    success_url = reverse_lazy('staff_forms:home')
    success_message = 'A leaver email have been sent to the relevant departments.'

    def form_valid(self, form):
        context = {'leaver': form.cleaned_data}
        subject = 'IT Leaver notification'
        html_message = render_to_string('staff_forms/leaver_mail_template.html', context)
        plain_message = strip_tags(html_message)
        from_email = 'personnel@conted.ox.ac.uk'
        cc_email = self.request.user.email
        cc = [cc_email]

        to = [settings.SUPPORT_EMAIL] if settings.DEBUG else []

        send_mail(subject, plain_message, from_email, to, cc, html_message=html_message)

        return super().form_valid(form)
