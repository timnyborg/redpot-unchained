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
from apps.enrolment.models import Enrolment
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
        feedback_years = {}
        for year in years:
            data = Feedback.objects.get_year_range(year).aggregate(
                teaching=Avg('rate_tutor'),
                content=Avg('rate_content'),
                facilities=Avg('rate_facilities'),
                admin=Avg('rate_admin'),
                catering=Avg('rate_refreshments'),
                accommodation=Avg('rate_accommodation'),
                average=Avg('avg_score'),
                sent=Count('id'),
                returned=Count('id', filter=Q(submitted__isnull=False)),
                high_scorers=Count('id', filter=Q(avg_score__gt=3.5)),
                total_scored=Count('id', filter=Q(avg_score__isnull=False)),
            )

            if data['total_scored']:
                data['satisfied'] = data['high_scorers'] / data['total_scored'] * 100

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
        year_data = self.object_list.aggregate(
            teaching=Avg('rate_tutor'),
            content=Avg('rate_content'),
            facilities=Avg('rate_facilities'),
            admin=Avg('rate_admin'),
            catering=Avg('rate_refreshments'),
            accommodation=Avg('rate_accommodation'),
            average=Avg('avg_score'),
            sent=Count('id'),
            returned=Count('id', filter=Q(submitted__isnull=False)),
            high_scorers=Count('id', filter=Q(avg_score__gt=3.5)),
            total_scored=Count('id', filter=Q(avg_score__isnull=False)),
        )

        # get year data objects
        year_data['year'] = self.year

        if year_data['total_scored']:
            year_data['satisfied'] = year_data['high_scorers'] / year_data['total_scored'] * 100

        context['year_data'] = year_data

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
        self.module = get_object_or_404(Module, code=self.kwargs['code'])
        self.object_list = self.get_queryset()
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        tutors_list = []
        tutors_set = self.module.tutor_modules.filter(is_teaching=True)
        for tutorobj in tutors_set:
            student_id = tutorobj.tutor.student.id
            tutor_name = tutorobj.tutor.student.firstname + ' ' + tutorobj.tutor.student.surname
            tutors_list.append((student_id, tutor_name))
        return {**kwargs, 'tutors_choices': tutors_list}

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

        results = self.object_list
        module_data = results.aggregate(
            teaching=Avg('rate_tutor'),
            content=Avg('rate_content'),
            facilities=Avg('rate_facilities'),
            admin=Avg('rate_admin'),
            catering=Avg('rate_refreshments'),
            accommodation=Avg('rate_accommodation'),
            average=Avg('avg_score'),
            sent=Count('id'),
            returned=Count('id', filter=Q(submitted__isnull=False)),
            high_scorers=Count('id', filter=Q(avg_score__gt=3.5)),
            total_scored=Count('id', filter=Q(avg_score__isnull=False)),
        )
        if module_data['total_scored']:
            module_data['satisfied'] = module_data['high_scorers'] / module_data['total_scored'] * 100

        context['module_score'] = module_data

        # get only submitted rows
        context['feedback'] = results.filter(submitted__isnull=False).order_by('submitted')
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
