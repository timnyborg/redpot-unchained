import datetime
import statistics

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Avg, Count, Q, Subquery
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import FormView, ListView

from apps.core.utils.views import PageTitleMixin
from apps.enrolment.models import Enrolment
from apps.module.models import Module

from . import services
from .forms import CommentAndReportForm, FeedbackRequestForm, PreviewQuestionnaireForm
from .models import Feedback, FeedbackAdmin


def home(request):
    return render(request, 'feedback/home.html')


class SiteTitleMixin(PageTitleMixin):
    title = 'Feedback'


def get_mean_value(list_of_ints):  # Takes a list of integers and returns a mean value
    value = round(statistics.mean(list_of_ints or [0]), 1)
    return value


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
                avg_accommodation=Avg('feedback__rate_accommodation'),
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
            module_set = Module.objects.filter(code=module_code)
            module_id = module_set[0]

            updated = datetime.datetime.now()
            current_user = self.request.user
            f = FeedbackAdmin(module=module_id, updated=updated, admin_comments=comments, person=current_user)
            f.save()

            # todo send feedback to staffs and add attachments
            send_mail('Subject here', 'Here is the message.', 'lokez21@gmail.com', ['lokez21@gmail.com'])

            messages.success(self.request, 'Your comment has been received. The tutor(s) has been sent an email')

        return super().form_valid(form)

    def get_subtitle(self):
        module_title = Feedback.objects.filter(module__code=self.code)[0].module.title
        return f'Results for {module_title}({self.code})'

    def get_queryset(self):
        return Feedback.objects.filter(module__code=self.code)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = self.object_list
        module = results[0].module
        context['module'] = module

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
        context['comments_list'] = FeedbackAdmin.objects.filter(module=module).order_by('updated')

        return context


class PreviewQuestionnaireView(LoginRequiredMixin, SiteTitleMixin, FormView):
    template_name = 'feedback/preview_questionnaire.html'
    model = Feedback
    form_class = PreviewQuestionnaireForm


class FeedbackRequestView(LoginRequiredMixin, SiteTitleMixin, FormView):
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
