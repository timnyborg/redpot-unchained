import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q, Subquery
from django.shortcuts import get_object_or_404, redirect, reverse
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import FormView, ListView

from apps.core.utils.views import PageTitleMixin
from apps.module.models import Module

from . import services
from .forms import CommentAndReportForm, FeedbackRequestForm, PreviewQuestionnaireForm
from .models import Feedback, FeedbackAdmin


class SiteTitleMixin(PageTitleMixin):
    title = 'Feedback'


class ResultListView(LoginRequiredMixin, SiteTitleMixin, ListView):
    subtitle = 'Results'
    template_name = 'feedback/results.html'
    context_object_name = 'results'

    def get_queryset(self):
        current_year = datetime.datetime.now().year
        four_year_results = Feedback.objects.get_year_range(current_year - 3, current_year)
        return four_year_results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = datetime.datetime.now().year

        years = range(current_year - 3, current_year + 1)
        feedback_years = {year: Feedback.objects.get_year_range(year).statistics() for year in years}
        context['feedback_years'] = feedback_years
        return context


class ResultYearListView(LoginRequiredMixin, SiteTitleMixin, ListView):
    template_name = 'feedback/results_year.html'
    model = Feedback

    def dispatch(self, *args, **kwargs):
        self.year = self.kwargs['year']
        return super().dispatch(*args, **kwargs)

    def get_subtitle(self):
        return f'Results - Academic Year ({self.year} - {self.year+1})'

    def get_queryset(self):
        return Feedback.objects.get_year_range(self.year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year_data'] = self.object_list.statistics()

        # get all the modules for the year
        modules = (
            Module.objects.order_by('code')
            .filter(id__in=Subquery(self.object_list.values('module')))
            .annotate(
                teaching=Avg('feedback__rate_tutor'),
                content=Avg('feedback__rate_content'),
                facilities=Avg('feedback__rate_facilities'),
                admin=Avg('feedback__rate_admin'),
                catering=Avg('feedback__rate_refreshments'),
                accom=Avg('feedback__rate_accommodation'),
                average=Avg('feedback__avg_score'),
                sent=Count('feedback__id'),
                returned=Count('feedback__id', filter=Q(feedback__submitted__isnull=False)),
                high_scorers=Count('feedback__id', filter=Q(feedback__avg_score__gt=3.5)),
                total_scored=Count('feedback__id', filter=Q(feedback__avg_score__isnull=False)),
            )
        )
        for module in modules:
            if module.total_scored:
                module.satisfied = module.high_scorers / module.total_scored * 100

        context['modules_list'] = modules
        return context


class ResultWeekListView(LoginRequiredMixin, SiteTitleMixin, ListView):
    template_name = 'feedback/this_week.html'
    model = Feedback

    def dispatch(self, *args, **kwargs):
        self.end_date = datetime.datetime.now().date()
        self.start_date = self.end_date - datetime.timedelta(days=7)
        return super().dispatch(*args, **kwargs)

    def get_subtitle(self):
        return f'Student feedback submitted between ({self.start_date} - {self.end_date})'

    def get_queryset(self):
        return Feedback.objects.filter(submitted__gt=self.start_date).order_by('submitted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feedback_set'] = self.object_list
        return context


class ResultModuleListView(LoginRequiredMixin, SiteTitleMixin, FormView):
    template_name = 'feedback/results_module.html'
    model = Feedback
    form_class = CommentAndReportForm

    def dispatch(self, *args, **kwargs):
        self.module = get_object_or_404(Module, code=self.kwargs['code'])
        self.object_list = self.get_queryset()
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tutors_set = self.module.tutor_modules.filter(is_teaching=True)
        tutors_choices = [(item.tutor.student.id, str(item.tutor.student)) for item in tutors_set]
        return {**kwargs, 'tutors_choices': tutors_choices}

    def get_success_url(self):
        return reverse('feedback:results-module', kwargs={'code': self.module.code})

    def form_valid(self, form):
        comments = form.cleaned_data['comments']
        tutors = form.cleaned_data['tutors']

        if comments or tutors:
            FeedbackAdmin.objects.create(
                module=self.module,
                updated=datetime.datetime.now(),
                admin_comments=comments,
                person=self.request.user.get_full_name(),
            )

            # todo send feedback to staffs and admin along with added attachments
            services.email_admin_report(self.module, tutors)
            if tutors:
                services.email_tutor_report(self.module, tutors)

            messages.success(self.request, 'Your comment has been received. The tutor(s) has been sent an email')

        return super().form_valid(form)

    def get_subtitle(self):
        return f'Results for {self.module.title}({self.module.code})'

    def get_queryset(self):
        return self.module.feedback_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = self.module
        context['module_score'] = self.object_list.statistics()

        # get only submitted rows
        context['feedback'] = self.object_list.filter(submitted__isnull=False).order_by('submitted')
        context['comments_list'] = self.module.feedbackadmin_set.order_by('updated')

        return context


class PreviewQuestionnaireFormView(LoginRequiredMixin, SiteTitleMixin, FormView):
    template_name = 'feedback/preview_questionnaire.html'
    model = Feedback
    form_class = PreviewQuestionnaireForm

    def form_valid(self, form):
        module_obj = form.cleaned_data['module_code']
        url = f'{settings.PUBLIC_APPS_URL}/feedback/submit/{module_obj.id}'
        return redirect(url)


class FeedbackRequestFormView(LoginRequiredMixin, SiteTitleMixin, FormView):
    template_name = 'feedback/feedback_request.html'
    model = Feedback
    form_class = FeedbackRequestForm

    def form_valid(self, form):
        module_obj = form.cleaned_data['module_code']
        return redirect(reverse('feedback:preview', kwargs={'module_id': module_obj.id}))


class PreviewView(LoginRequiredMixin, SiteTitleMixin, ListView):
    template_name = 'feedback/preview.html'
    model = Feedback

    def dispatch(self, *args, **kwargs):
        self.module_id = self.kwargs.get('module_id')
        self.module = get_object_or_404(Module, id=self.module_id)
        return super().dispatch(*args, **kwargs)

    def get_subtitle(self):
        return f'{self.module.title} - {self.module.code}'

    def get_queryset(self):
        # Build a query for fetching students on modules:
        module_students = (
            self.module.enrolments.filter(status__in=[10, 71, 90])
            .select_related('module', 'qa', 'qa__student')
            .order_by('qa__student__email__email')
        )

        return module_students

    def email_preview(self, list_dict: list):
        for item in list_dict:
            firstname = item['firstname']
            if item['action'] == 'Notify':
                return render_to_string(
                    'feedback/email/feedback_email.html',
                    {'firstname': firstname, 'module_title': self.module.title, 'module_id': self.module.id},
                )

            elif item['action'] == 'Remind':
                return render_to_string(
                    'feedback/email/feedback_email_reminder.html',
                    {'firstname': firstname, 'module_title': self.module.title, 'module_id': self.module.id},
                )

            elif item['action'] == 'Reminder sent (Skip)':
                return 'Reminder already sent to students.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        enrolments = self.object_list
        list_dict = []
        today = datetime.datetime.now()
        for enrolment in enrolments:
            email = enrolment.qa.student.get_default_email().email
            action = 'Notify'

            student_feedback = Feedback.objects.filter(enrolment=enrolment.id).first()
            if not email:
                action = 'The student has no Email address. (Skip)'
            else:
                if student_feedback:
                    if today.date() == student_feedback.notified.date():
                        # Prevent sending reminder on same day of notification!
                        action = 'Notification just sent today. (Skip)'
                    elif not student_feedback.reminder:
                        action = 'Remind'
                    elif student_feedback.reminder:
                        action = 'Reminder sent (Skip)'
                    if student_feedback.submitted:
                        action = 'Submitted (Skip)'

            list_dict.append(
                {
                    'student_id': enrolment.qa.student.id,
                    'firstname': enrolment.qa.student.firstname,
                    'surname': enrolment.qa.student.surname,
                    'email': email,
                    'action': action,
                }
            )

        context['list_dict'] = list_dict
        context['module_id'] = self.module.id
        context['Send_email_button'] = False
        if list_dict and list_dict[0]['action'] in ['Remind', 'Notify']:
            context['Send_email_button'] = True

        context['email_preview'] = self.email_preview(list_dict)
        return context


class RequestFeedback(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        module = get_object_or_404(Module, id=self.kwargs['module_id'])
        services.process_and_send_emails(module)
        messages.success(request, 'The email has been sent to students')
        return redirect(reverse('feedback:results-module', kwargs={'code': module.code}))


class RecentlyCompletedOrFinishingSoon(LoginRequiredMixin, SiteTitleMixin, ListView):
    template_name = 'feedback/recently_completed_or_finishing_soon.html'
    model = Module
    subtitle = 'Courses that have recently finished, or will finish soon.'

    def get_queryset(self):
        start_date = datetime.date.today() - datetime.timedelta(days=14)  # get courses for 14 days in the past
        end_date = datetime.date.today() + datetime.timedelta(days=2)  # get courses for 2 days in the future
        return (
            Module.objects.filter(~Q(status=33), end_date__range=[start_date, end_date])
            .values('id', 'code', 'title', 'end_date', 'email')
            .order_by('end_date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        modules_list = self.object_list
        modules = []
        for module in modules_list:
            if Feedback.objects.filter(module=module['id']).count() > 0:
                module['status'] = 'Send reminder'
                if Feedback.objects.filter(module=module['id'], reminder__isnull=False).exists():
                    module['status'] = 'See results'
            else:
                module['status'] = 'Send feedback request'
            modules.append(module)

        context['modules'] = modules
        return context


class ExportToExcel(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        module = get_object_or_404(Module, id=kwargs['module_id'])
        return services.export_users_xls(module)
