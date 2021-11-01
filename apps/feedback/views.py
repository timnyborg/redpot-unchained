import datetime
import statistics

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views import View
from django.views.generic import FormView, ListView

from apps.core.utils.views import PageTitleMixin
from apps.enrolment.models import Enrolment
from apps.module.models import Module

from .forms import CommentAndReportForm, FeedbackRequestForm, PreviewQuestionnaireForm
from .models import Feedback, FeedbackAdmin


class SiteTitleMixin(PageTitleMixin):
    title = 'Feedback'


def home(request):
    return render(request, 'feedback/home.html')


def get_mean_value(list_of_ints):  # Takes a list of integers and returns a mean value
    value = round(statistics.mean(list_of_ints or [0]), 1)
    return value


class ResultListView(LoginRequiredMixin, SiteTitleMixin, ListView):
    subtitle = 'Results'
    template_name = 'feedback/results.html'
    context_object_name = 'results'

    def get_queryset(self):
        current_year = datetime.datetime.now().year
        from_year = current_year - 3
        four_year_results = Feedback.objects.filter(
            module__start_date__gt=str(from_year) + '-08-31', module__start_date__lt=str(current_year + 1) + '-09-01'
        )
        return four_year_results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = datetime.datetime.now().year
        from_year = current_year - 3

        years = range(from_year, current_year + 1)
        feedback_years = {}
        for year in years:
            year_fields = self.object_list.filter(
                module__start_date__gt=str(year) + '-08-31', module__start_date__lt=str(year + 1) + '-09-01'
            )
            data = {}
            data['avg_teaching'] = get_mean_value(
                year_fields.values_list('rate_tutor', flat=True).filter(rate_tutor__gt=0)
            )
            data['avg_content'] = get_mean_value(
                year_fields.values_list('rate_content', flat=True).filter(rate_content__gt=0)
            )
            data['avg_facilities'] = get_mean_value(
                year_fields.values_list('rate_facilities', flat=True).filter(rate_facilities__gt=0)
            )
            data['avg_admin'] = get_mean_value(
                year_fields.values_list('rate_admin', flat=True).filter(rate_admin__gt=0)
            )
            data['avg_catering'] = get_mean_value(
                year_fields.values_list('rate_refreshments', flat=True).filter(rate_refreshments__gt=0)
            )
            data['avg_accommodation'] = get_mean_value(
                year_fields.values_list('rate_accommodation', flat=True).filter(rate_accommodation__gt=0)
            )
            data['average'] = get_mean_value(
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
        year_results = Feedback.objects.filter(
            module__start_date__gt=str(self.year) + '-08-31', module__start_date__lt=str(self.year + 1) + '-09-01'
        )
        return year_results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year_results = self.object_list

        year = self.year
        # get year data objects
        year_data = {}
        year_data['year'] = year
        year_data['avg_teaching'] = get_mean_value(
            year_results.values_list('rate_tutor', flat=True).filter(rate_tutor__gt=0)
        )
        year_data['avg_content'] = get_mean_value(
            year_results.values_list('rate_content', flat=True).filter(rate_content__gt=0)
        )
        year_data['avg_facilities'] = get_mean_value(
            year_results.values_list('rate_facilities', flat=True).filter(rate_facilities__gt=0)
        )
        year_data['avg_admin'] = get_mean_value(
            year_results.values_list('rate_admin', flat=True).filter(rate_admin__gt=0)
        )
        year_data['avg_catering'] = get_mean_value(
            year_results.values_list('rate_refreshments', flat=True).filter(rate_refreshments__gt=0)
        )
        year_data['avg_accommodation'] = get_mean_value(
            year_results.values_list('rate_accommodation', flat=True).filter(rate_accommodation__gt=0)
        )
        year_data['average'] = get_mean_value(
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
            module_data['avg_teaching'] = get_mean_value(
                module_results.values_list('rate_tutor', flat=True).filter(rate_tutor__gt=0)
            )
            module_data['avg_content'] = get_mean_value(
                module_results.values_list('rate_content', flat=True).filter(rate_content__gt=0)
            )
            module_data['avg_facilities'] = get_mean_value(
                module_results.values_list('rate_facilities', flat=True).filter(rate_facilities__gt=0)
            )
            module_data['avg_admin'] = get_mean_value(
                module_results.values_list('rate_admin', flat=True).filter(rate_admin__gt=0)
            )
            module_data['avg_catering'] = get_mean_value(
                module_results.values_list('rate_refreshments', flat=True).filter(rate_refreshments__gt=0)
            )
            module_data['avg_accommodation'] = get_mean_value(
                module_results.values_list('rate_accommodation', flat=True).filter(rate_accommodation__gt=0)
            )
            module_data['average'] = get_mean_value(
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
        module_results = Feedback.objects.filter(module__code=self.code)
        return module_results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = self.object_list

        module_id = results[0].module.id
        module_title = results[0].module.title

        module_data = {}
        module_data['title'] = module_title
        module_data['avg_teaching'] = get_mean_value(
            results.values_list('rate_tutor', flat=True).filter(rate_tutor__gt=0)
        )
        module_data['avg_content'] = get_mean_value(
            results.values_list('rate_content', flat=True).filter(rate_content__gt=0)
        )
        module_data['avg_facilities'] = get_mean_value(
            results.values_list('rate_facilities', flat=True).filter(rate_facilities__gt=0)
        )
        module_data['avg_admin'] = get_mean_value(
            results.values_list('rate_admin', flat=True).filter(rate_admin__gt=0)
        )
        module_data['avg_catering'] = get_mean_value(
            results.values_list('rate_refreshments', flat=True).filter(rate_refreshments__gt=0)
        )
        module_data['avg_accommodation'] = get_mean_value(
            results.values_list('rate_accommodation', flat=True).filter(rate_accommodation__gt=0)
        )
        module_data['average'] = get_mean_value(
            [
                module_data['avg_teaching'],
                module_data['avg_content'],
                module_data['avg_facilities'],
                module_data['avg_admin'],
                module_data['avg_catering'],
                module_data['avg_accommodation'],
            ]
        )
        module_data['sent'] = results.count()
        module_data['returned'] = results.filter(submitted__isnull=False).count()
        high_scorers = results.filter(avg_score__gt=3.5).count()
        total_scored = results.filter(avg_score__isnull=False).count()

        try:
            module_data['satisfied'] = int(float(high_scorers) / float(total_scored) * 100)
        except ZeroDivisionError:
            module_data['satisfied'] = None

        context['module_score'] = module_data

        feedback_results = results.filter(submitted__isnull=False).order_by('submitted')  # get only submitted rows
        feedback_data_list = {}

        for feedback_result in feedback_results:
            feedback_data = {}
            feedback_data['id'] = feedback_result.id
            feedback_data['student_name'] = feedback_result.your_name if feedback_result.your_name else 'Anonymous'
            feedback_data['submitted_on'] = feedback_result.submitted.strftime('%H:%M on %d-%b-%Y')
            feedback_data['average'] = round(float(feedback_result.avg_score), 1)
            feedback_data['teaching'] = feedback_result.rate_tutor
            feedback_data['content'] = feedback_result.rate_content
            feedback_data['facilities'] = feedback_result.rate_facilities
            feedback_data['admin'] = feedback_result.rate_admin
            feedback_data['catering'] = feedback_result.rate_refreshments
            feedback_data['accommodation'] = feedback_result.rate_accommodation
            feedback_data['comment'] = feedback_result.comments

            feedback_data_list[feedback_data['id']] = feedback_data

        context['feedback_data_list'] = feedback_data_list

        comments_list = []
        admin_comments_set = FeedbackAdmin.objects.filter(module=module_id).order_by('updated')
        for comment_row in admin_comments_set:
            values = {}
            values['comment'] = comment_row.admin_comments
            values['uploaded_by'] = comment_row.person
            values['uploaded_on'] = (
                comment_row.updated.strftime('%H:%M on %d-%b-%Y')
                if isinstance(comment_row.updated, datetime.date)
                else '-'
            )
            comments_list.append(values)
        context['comments_list'] = comments_list

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
        self.module = Module.objects.get(id=self.module_id)
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
    model = Feedback

    def post(self, request, *args, **kwargs):
        self.module_id = self.kwargs['module_id']
        self.module = Module.objects.get(id=self.module_id)
        self.module_contact = self.module.email if '@conted' in self.module.email else self.module.portfolio.email
        self.module_students = (
            Enrolment.objects.filter(
                module=self.module,
                status__in=[10, 71, 90],
                qa__student__email__email__isnull=False,
                qa__student__email__is_default=True,
            )
            .select_related('module', 'qa', 'qa__student', 'qa__student__email')
            .values(
                'qa__student__id',
                'qa__student__firstname',
                'qa__student__surname',
                'id',
                'qa__student__email__email',
                'module',
                'module__id',
                'module__title',
                'module__code',
                'module__email',
                'module__portfolio__email',
            )
            .order_by(
                '-qa__student__email__email',
                'qa__student__surname',
                'qa__student__firstname',
            )
        )

        self.process_and_send_emails(self.module_students)
        messages.success(self.request, 'The email has been sent to students')
        return redirect(
            reverse('feedback:results-module', kwargs={'code': self.module_students.first()['module__code']})
        )

    def process_and_send_emails(self, module_students):
        email_context = {}
        for student in module_students:
            email_context['firstname'] = student['qa__student__firstname']
            email_context['email'] = student['qa__student__email__email']
            email_context['module'] = student['module']
            email_context['module_id'] = student['module__id']
            email_context['module_title'] = student['module__title']
            email_context['enrolment'] = student['id']
            mod_contact = student['module__email'] if student['module__email'] else student['module__portfolio__email']

            student_feedback = Feedback.objects.filter(enrolment=email_context['enrolment'])

            if not student_feedback:
                subject = 'Your feedback on ' + email_context['module_title']
                html_message = render_to_string('feedback/email/feedback_email.html', email_context)
                plain_message = strip_tags(html_message)
                from_email = mod_contact
                cc_email = self.request.user.email
                cc = [cc_email]
                to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [email_context['email']]
                send_mail(subject, plain_message, from_email, to, cc, html_message=html_message)

                # Create object in table if object didn't exist
                Feedback.objects.create(
                    module=Module.objects.get(id=email_context['module_id']),
                    enrolment=email_context['enrolment'],
                    notified=datetime.datetime.now(),
                )

            elif not student_feedback.first().reminder:
                subject = 'Your feedback on ' + email_context['module_title']
                html_message = render_to_string('feedback/email/feedback_email_reminder.html', email_context)
                plain_message = strip_tags(html_message)
                from_email = mod_contact
                cc_email = self.request.user.email
                cc = [cc_email]
                to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [email_context['email']]
                send_mail(subject, plain_message, from_email, to, cc, html_message=html_message)
                Feedback.objects.filter(enrolment=email_context['enrolment']).update(reminder=datetime.datetime.now())
