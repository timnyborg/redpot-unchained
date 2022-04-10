import datetime
from pathlib import Path

from weasyprint import CSS, HTML

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import FormView, ListView

from apps.core.utils.views import PageTitleMixin
from apps.enrolment.models import Enrolment
from apps.module.models import Module

from ..core.utils.strings import normalize
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
        from_year = current_year - 3

        years = range(from_year, current_year + 1)
        feedback_years = {}
        for year in years:
            year_fields = Feedback.objects.get_year_range(year)
            data = {}
            data['avg_teaching'] = services.get_mean_value(
                year_fields.values_list('rate_tutor', flat=True).filter(rate_tutor__gt=0)
            )
            data['avg_content'] = services.get_mean_value(
                year_fields.values_list('rate_content', flat=True).filter(rate_content__gt=0)
            )
            data['avg_facilities'] = services.get_mean_value(
                year_fields.values_list('rate_facilities', flat=True).filter(rate_facilities__gt=0)
            )
            data['avg_admin'] = services.get_mean_value(
                year_fields.values_list('rate_admin', flat=True).filter(rate_admin__gt=0)
            )
            data['avg_catering'] = services.get_mean_value(
                year_fields.values_list('rate_refreshments', flat=True).filter(rate_refreshments__gt=0)
            )
            data['avg_accommodation'] = services.get_mean_value(
                year_fields.values_list('rate_accommodation', flat=True).filter(rate_accommodation__gt=0)
            )
            data['average'] = services.get_mean_value(  # todo get the database to do the averaging work
                [
                    data['avg_teaching'],
                    data['avg_content'],
                    data['avg_facilities'],
                    data['avg_admin'],
                    data['avg_catering'],
                    data['avg_accommodation'],
                ]
            )
            data['sent'] = year_fields.count()
            data['returned'] = year_fields.filter(submitted__isnull=False).count()
            high_scorers = year_fields.filter(avg_score__gt=3.5).count()
            total_scored = year_fields.filter(avg_score__isnull=False).count()

            try:
                data['satisfied'] = int(float(high_scorers) / float(total_scored) * 100)
            except ZeroDivisionError:
                data['satisfied'] = None

            feedback_years[year] = data
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
        year_results = self.object_list

        year = self.year
        # get year data objects
        year_data = {}

        year_data['year'] = year
        year_data['avg_teaching'] = services.get_mean_value(
            year_results.values_list('rate_tutor', flat=True).filter(rate_tutor__gt=0)
        )
        year_data['avg_content'] = services.get_mean_value(
            year_results.values_list('rate_content', flat=True).filter(rate_content__gt=0)
        )
        year_data['avg_facilities'] = services.get_mean_value(
            year_results.values_list('rate_facilities', flat=True).filter(rate_facilities__gt=0)
        )
        year_data['avg_admin'] = services.get_mean_value(
            year_results.values_list('rate_admin', flat=True).filter(rate_admin__gt=0)
        )
        year_data['avg_catering'] = services.get_mean_value(
            year_results.values_list('rate_refreshments', flat=True).filter(rate_refreshments__gt=0)
        )
        year_data['avg_accommodation'] = services.get_mean_value(
            year_results.values_list('rate_accommodation', flat=True).filter(rate_accommodation__gt=0)
        )
        year_data['average'] = services.get_mean_value(
            [
                year_data['avg_teaching'],
                year_data['avg_content'],
                year_data['avg_facilities'],
                year_data['avg_admin'],
                year_data['avg_catering'],
                year_data['avg_accommodation'],
            ]
        )
        year_data['sent'] = year_results.count()
        year_data['returned'] = year_results.filter(submitted__isnull=False).count()
        high_scorers = year_results.filter(avg_score__gt=3.5).count()
        total_scored = year_results.filter(avg_score__isnull=False).count()

        try:
            year_data['satisfied'] = int(float(high_scorers) / float(total_scored) * 100)
        except ZeroDivisionError:
            year_data['satisfied'] = None

        context['year_data'] = year_data

        # get all the modules for the year
        year_modules = year_results.order_by('module__code').values_list('module', flat=True).distinct()
        modules_data = {}

        for module in year_modules:
            module_results = year_results.filter(module=module)
            module_data = {}
            module_code = module_results[0].module.code
            module_data['module_title'] = module_results[0].module.title
            module_data['avg_teaching'] = services.get_mean_value(
                module_results.values_list('rate_tutor', flat=True).filter(rate_tutor__gt=0)
            )
            module_data['avg_content'] = services.get_mean_value(
                module_results.values_list('rate_content', flat=True).filter(rate_content__gt=0)
            )
            module_data['avg_facilities'] = services.get_mean_value(
                module_results.values_list('rate_facilities', flat=True).filter(rate_facilities__gt=0)
            )
            module_data['avg_admin'] = services.get_mean_value(
                module_results.values_list('rate_admin', flat=True).filter(rate_admin__gt=0)
            )
            module_data['avg_catering'] = services.get_mean_value(
                module_results.values_list('rate_refreshments', flat=True).filter(rate_refreshments__gt=0)
            )
            module_data['avg_accommodation'] = services.get_mean_value(
                module_results.values_list('rate_accommodation', flat=True).filter(rate_accommodation__gt=0)
            )
            module_data['average'] = services.get_mean_value(
                [
                    module_data['avg_teaching'],
                    module_data['avg_content'],
                    module_data['avg_facilities'],
                    module_data['avg_admin'],
                    module_data['avg_catering'],
                    module_data['avg_accommodation'],
                ]
            )
            module_data['sent'] = module_results.count()
            module_data['returned'] = module_results.filter(submitted__isnull=False).count()
            high_scorers = module_results.filter(avg_score__gt=3.5).count()
            total_scored = module_results.filter(avg_score__isnull=False).count()

            try:
                module_data['satisfied'] = int(float(high_scorers) / float(total_scored) * 100)
            except ZeroDivisionError:
                module_data['satisfied'] = None

            modules_data[module_code] = module_data

        context['modules_list'] = modules_data
        return context


class ResultWeekListView(LoginRequiredMixin, SiteTitleMixin, ListView):
    template_name = 'feedback/this_week.html'
    model = Feedback

    def dispatch(self, *args, **kwargs):
        self.end_date = datetime.datetime.now().date()
        self.start_date = self.end_date - datetime.timedelta(days=6)
        return super().dispatch(*args, **kwargs)

    def get_subtitle(self):
        return f'Student feedback submitted between ({self.start_date} - {self.end_date})'

    def get_queryset(self):
        return Feedback.objects.filter(submitted__gt=self.start_date).order_by('submitted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feedback_list = self.object_list

        feedback_set = {}
        for feedback in feedback_list:
            feedback_dict = {}

            feedback_dict['feedback_id'] = feedback.id
            feedback_dict['module_code'] = feedback.module.code
            feedback_dict['module_title'] = feedback.module.title
            feedback_dict['submitted_on'] = feedback.submitted.strftime('%H:%M on %d-%b-%Y')
            feedback_dict['student_name'] = feedback.your_name if feedback.your_name else 'Anonymous'
            feedback_dict['rate_tutor'] = feedback.rate_tutor
            feedback_dict['rate_content'] = feedback.rate_content
            feedback_dict['rate_admin'] = feedback.rate_admin
            feedback_dict['rate_facility'] = feedback.rate_facilities
            feedback_dict['rate_accommodation'] = feedback.rate_accommodation
            feedback_dict['rate_refreshments'] = feedback.rate_refreshments
            feedback_dict['average'] = round(float(feedback.avg_score or 0), 1)
            feedback_dict['comment'] = feedback.comments
            tutors = feedback.module.tutor_modules.all().order_by('tutor')
            feedback_dict['tutors_list'] = [
                f'{tutor.tutor.student.firstname} {tutor.tutor.student.surname}' for tutor in tutors
            ]
            feedback_set[feedback_dict['feedback_id']] = feedback_dict

            context['feedback_set'] = feedback_set
        return context


class ResultModuleListView(LoginRequiredMixin, SiteTitleMixin, FormView):
    template_name = 'feedback/results_module.html'
    model = Feedback
    form_class = CommentAndReportForm

    def dispatch(self, *args, **kwargs):
        self.code = self.kwargs['code']
        self.object_list = self.get_queryset()
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        results = self.object_list
        tutors_list = []
        tutors_set = results[0].module.tutor_modules.filter(is_teaching=True)
        for tutorobj in tutors_set:
            student_id = tutorobj.tutor.student.id
            tutor_name = tutorobj.tutor.student.firstname + ' ' + tutorobj.tutor.student.surname
            tutors_list.append((student_id, tutor_name))
        return {**kwargs, 'tutors_choices': tutors_list}

    def get_success_url(self):
        return reverse('feedback:results-module', kwargs={'code': self.code})

    def form_valid(self, form):
        comments = form.cleaned_data['comments']
        tutors = form.cleaned_data['tutors']

        if comments or tutors:
            module_code = self.kwargs['code']
            module = Module.objects.get(code=module_code)

            updated = datetime.datetime.now()
            current_user = self.request.user
            f = FeedbackAdmin(module=module, updated=updated, admin_comments=comments, person=current_user)
            f.save()

            # todo send feedback to staffs and admin along with added attachments
            services.email_admin_report(module, tutors)
            if tutors:
                services.email_tutor_report(module, tutors)

            messages.success(self.request, 'Your comment has been received. The tutor(s) has been sent an email')

        return super().form_valid(form)

    def get_subtitle(self):
        module_title = Feedback.objects.filter(module__code=self.code)[0].module.title
        return f'Results for {module_title}({self.code})'

    def get_queryset(self):
        module_results = Feedback.objects.filter(module__code=self.code)
        return module_results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module_id = self.object_list.first().module.id

        context['module_info'] = services.get_module_info(module_id)
        context['module_summary'] = services.get_module_summary(module_id)
        context['feedback_data_dict'] = services.get_module_feedback_details(module_id)
        context['comments_list'] = services.get_module_comments(module_id)

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
        module_title = self.module.title
        module_code = self.module.code
        return f'{module_title} - {module_code}'

    def get_queryset(self):
        # Build a query for fetching students on modules:
        module_students = (
            Enrolment.objects.filter(module=self.module_id, status__in=[10, 71, 90])
            .select_related('module', 'qa', 'qa__student', 'qa__student__email', 'status__description')
            .values(
                'qa__student__id',
                'qa__student__firstname',
                'qa__student__surname',
                'id',
                'status__description',
                'qa__student__email__id',
                'qa__student__email__email',
                'module',
            )
            .order_by(
                '-qa__student__email__email',
                'qa__student__surname',
                'qa__student__firstname',
            )
        )

        return module_students

    def email_preview(self, list_dict=None):
        if list_dict:
            for item in list_dict:
                firstname = item['firstname']
                module_id = item['module_id']
                module = Module.objects.filter(id=module_id).first()
                module_title = module.title
                if item['action'] == 'Notify':
                    return render_to_string(
                        'feedback/email/feedback_email.html',
                        {'firstname': firstname, 'module_title': module_title, 'module_id': module_id},
                    )

                elif item['action'] == 'Remind':
                    return render_to_string(
                        'feedback/email/feedback_email_reminder.html',
                        {'firstname': firstname, 'module_title': module_title, 'module_id': module_id},
                    )

                elif item['action'] == 'Reminder sent (Skip)':
                    return 'Reminder already sent to students.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        students = self.object_list
        list_dict = []
        today = datetime.datetime.now()
        for student in students:
            email = student['qa__student__email__email']
            firstname = student['qa__student__firstname']
            surname = student['qa__student__surname']
            student_id = student['qa__student__id']
            email_id = student['qa__student__email__id']
            module_id = student['module']
            action = 'Notify'

            if not email:
                action = 'The student has no Email address. (Skip)'
            else:
                student_feedback = Feedback.objects.filter(hash_id=student['id'])
                if student_feedback.first():
                    if str(today) in str(
                        student_feedback.first().notified
                    ):  # Prevent sending reminder on same day of notification!
                        action = 'Notification just sent today. (Skip)'
                    elif student_feedback.first().reminder is None:
                        action = 'Remind'
                    elif student_feedback.first().reminder is not None:
                        action = 'Reminder sent (Skip)'

                    if student_feedback.first().submitted is not None:
                        action = 'Submitted (Skip)'

            list_dict.append(
                {
                    'student_id': student_id,
                    'firstname': firstname,
                    'surname': surname,
                    'email': email,
                    'email_id': email_id,
                    'module_id': module_id,
                    'action': action,
                }
            )

        context['list_dict'] = list_dict
        context['module_id'] = self.module_id
        context['Send_email_button'] = False
        if list_dict:
            if list_dict[0]['action'] in ['Remind', 'Notify']:
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
    subtitle = 'Courses that have recently finished, or will finish soon..'

    def dispatch(self, *args, **kwargs):
        self.past_days = 14  # get courses for 14 days in the past
        self.future_days = 2  # get courses for 2 days in the future
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        start_date = datetime.date.today() - datetime.timedelta(days=self.past_days)
        end_date = datetime.date.today() + datetime.timedelta(days=self.future_days)
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
                if Feedback.objects.filter(module=module['id'], reminder__isnull=False).count() > 0:
                    module['status'] = 'See results'
            else:
                module['status'] = 'Send feedback request'
            modules.append(module)

        context['modules'] = modules
        return context


class ExportToExcel(View):
    def get(self, request, *args, **kwargs):
        module_id = kwargs['module_id']
        return services.export_users_xls(module_id)


def make_pdf(request, **kwargs):
    module_id = kwargs['module_id']
    module = get_object_or_404(Module, id=module_id)
    filename = normalize(f"feedback_report_{module.title}_{module.code}.pdf")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{filename}"'

    context = {
        'module_info': services.get_module_info(module_id),
        'module_summary': services.get_module_summary(module_id),
        'tutors': services.get_module_tutors(module_id),
        'feedback_data_dict': services.get_module_feedback_details(module_id),
        'comments_list': services.get_module_comments(module_id),
        'context_data': 'This is a context data',
        'module_summary_headers': [
            'Module Title',
            'Satisfied(%)',
            'Average',
            'Teaching',
            'Content',
            'Facilities',
            'Admin',
            'Catering',
            'Accomm',
            'Sent',
            'Returned',
        ],
    }
    # font_config = FontConfiguration() #todo clarify with Tim
    html_doc = render_to_string('feedback/pdfs/module_feedback.html', context=context)
    HTML(string=html_doc).write_pdf(response, stylesheets=[CSS(Path(__file__).parent / 'static/css/pdf.css')])
    return response
