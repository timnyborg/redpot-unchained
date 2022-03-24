from datetime import datetime, timedelta

from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core import mail
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views import generic

from apps.core.utils.views import PageTitleMixin
from apps.module.models import Module
from apps.student.models import Student
from apps.waitlist import forms, models


class Add(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    model = models.Waitlist
    form_class = forms.WaitlistForm
    subtitle = 'Add'
    success_message = 'Student added to waiting list'
    template_name = 'core/form.html'

    def get_initial(self) -> dict:
        return {'student': get_object_or_404(Student, pk=self.kwargs['student_id'])}

    def get_success_url(self) -> str:
        return self.object.module.get_absolute_url() + '#waitlist'


class Delete(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = models.Waitlist
    success_message = 'Student removed from waiting list'
    template_name = 'core/delete_form.html'

    def get_success_url(self) -> str:
        messages.success(self.request, self.success_message)
        return self.object.module.get_absolute_url() + '#waitlist'


class EmailSingle(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        waitlist_spot = models.Waitlist.objects.get(pk=self.kwargs['pk'])
        module = waitlist_spot.module
        redirect_target = module.get_absolute_url() + '#waitlist'

        email_row = waitlist_spot.student.get_default_email()
        if not email_row:
            messages.error(request, 'Student has no email address')
            return redirect(redirect_target)

        # todo: convert this check into a mixin, since it's used wherever we email the user
        if not request.user.email:
            messages.error(request, 'You do not have an email address defined in your profile')
            return redirect(redirect_target)

        context = {
            'student': waitlist_spot.student,
            'student_email': email_row.email,
            'module': module,
            'due_date': module.start_date + timedelta(days=2),
            'sender': models.OFFICES.get(module.portfolio_id, request.user.get_full_name()),
        }
        body = render_to_string('waitlist/email/single.html', context=context)

        mail.send_mail(
            recipient_list=[settings.SUPPORT_EMAIL] if settings.DEBUG else [request.user.email],
            from_email=settings.SUPPORT_EMAIL,
            subject=f'A place is now available on {module.title}',
            message=strip_tags(body),
            html_message=body,
        )

        waitlist_spot.emailed_on = datetime.now()
        waitlist_spot.save()

        messages.success(request, 'Email sent to your inbox for review')
        return redirect(redirect_target)


class EmailMultiple(LoginRequiredMixin, generic.View):
    """Email multiple students on a waitlist, whether for newly-opened spots, or a brand new run"""

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        # `module` is the module for which there are spaces
        # `source` is the module whose waiting list we're contacting (either the same module, or a previous run).
        module = get_object_or_404(Module, pk=self.kwargs['module'])
        new_run = 'previous_module' in self.kwargs
        if new_run:
            source = get_object_or_404(Module, pk=self.kwargs['previous_module'])
        else:
            source = module

        redirect_target = source.get_absolute_url() + '#waitlist'

        # Get email list from listed module, not new run
        waitlist_spots = models.Waitlist.objects.filter(module=source, student__email__is_default=True)

        # limit by selections
        if 'limited' in request.GET:
            ids = [int(val) for val in request.GET.getlist('id') if val.isnumeric()]
            waitlist_spots = waitlist_spots.filter(id__in=ids)

        # Emails everyone on the waiting list (or) on the selected list
        student_emails = waitlist_spots.values_list('student__email__email', flat=True)

        if not student_emails:
            messages.error(request, 'No valid students selected')
            return redirect(redirect_target)
        if not request.user.email:
            messages.error(request, 'You do not have an email address defined in your profile')
            return redirect(redirect_target)

        tutor_on_module = module.tutor_modules.filter(is_teaching=True).order_by('display_order').first()

        context = {
            'student_emails': student_emails,
            'new_run': new_run,
            'module': module,
            'tutor': tutor_on_module.tutor.student,
            'sender': models.OFFICES.get(module.portfolio_id, request.user.get_full_name()),
        }
        body = render_to_string('waitlist/email/multiple.html', context=context)

        subject = 'Re-run of ' if new_run else 'Place(s) now available'
        subject += f' on {module.title} ({module.start_date:%d %b %Y})'

        mail.send_mail(
            recipient_list=[settings.SUPPORT_EMAIL] if settings.DEBUG else [request.user.email],
            from_email=settings.SUPPORT_EMAIL,
            subject=subject,
            message=strip_tags(body),
            html_message=body,
        )

        waitlist_spots.update(emailed_on=datetime.now())
        messages.success(request, 'Email sent to your inbox for review')

        return redirect(redirect_target)
