from urllib.parse import urlencode

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.db.models import Prefetch, Q
from django.forms import Form
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic

from apps.core.utils import strings
from apps.core.utils.views import AutoTimestampMixin, DeletionFailedMessageMixin, PageTitleMixin
from apps.enrolment.models import Enrolment
from apps.tutor.models import Tutor

from . import datatables, forms, pdfs, services
from .models import Address, Diet, Email, EmergencyContact, Enquiry, MoodleID, OtherID, Phone, Student, StudentArchive


class Create(LoginRequiredMixin, generic.View):
    def create_student(self, **kwargs) -> Student:
        signature_fields = {
            'modified_by': self.request.user.username,
            'created_by': self.request.user.username,
        }
        student = Student.objects.create(**kwargs, **signature_fields)
        if 'email' in kwargs:
            Email.objects.create(student=student, email=kwargs['email'], is_default=True, **signature_fields)
        return student

    def get_queryset(self, form: forms.CreatePersonSearchForm):
        """Take the values from the search form and produce a custom queryset"""
        # Reusable matching rules.  Could be annotations?
        NO_MATCH = Q(pk=0)
        firstname_match = Q(firstname__contains=form.cleaned_data['firstname']) | Q(
            nickname__contains=form.cleaned_data['firstname']
        )
        surname_match = Q(surname__contains=form.cleaned_data['surname'])
        # Avoid matching on empty values
        birthdate_match = Q(birthdate=form.cleaned_data['birthdate']) if form.cleaned_data['birthdate'] else NO_MATCH
        email_match = Q(email__email=form.cleaned_data['email']) if form.cleaned_data['email'] else NO_MATCH

        # Three matching options.
        match_query = (
            (firstname_match & (surname_match | birthdate_match)) | (surname_match & birthdate_match) | email_match
        )
        # Bring in email and default postcode for display in the table
        return Student.objects.filter(match_query).annotate(
            email_address=models.F('email__email'),
            default_address=models.FilteredRelation('address', condition=models.Q(address__is_default=True)),
            postcode=models.F('default_address__postcode'),
        )[:30]

    def get(self, request):
        search_form = forms.CreatePersonSearchForm()
        return render(request, 'student/new.html', {'search_form': search_form})

    def post(self, request):
        table = None
        search_form = forms.CreatePersonSearchForm(request.POST)
        # Dummy form for the submit button. Could be stripped out?
        create_form = Form(request.POST, prefix='create')

        if search_form.is_valid():
            # Components of our search query
            queryset = self.get_queryset(search_form)
            table = datatables.CreateMatchTable(data=queryset, request=request)
            # Store details for use by creation method
            self.request.session['new_student'] = search_form.cleaned_data

        if self.request.POST.get('action') == 'create' and 'new_student' in self.request.session:
            student = self.create_student(**self.request.session['new_student'])
            del self.request.session['new_student']
            messages.success(request, message='Record created.  Please complete their information.')
            return redirect(student.get_absolute_url(), {'new': True})

        return render(
            request, 'student/new.html', {'search_form': search_form, 'create_form': create_form, 'table': table}
        )


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    title = 'Person'
    subtitle = 'Search'
    template_name = 'student/search.html'

    table_class = datatables.SearchTable
    filterset_class = datatables.SearchFilter

    # A bit complicated, since this search tool also searches on email, phone, address, which are one-to-many relations
    queryset = Student.objects.annotate(
        # Creates a left join with a condition.  The resulting relation can be used in annotations or
        # django-filter filters, e.g. django_filter.Column(..., field_name='default_address__postcode', ...)
        default_address=models.FilteredRelation('address', condition=models.Q(address__is_default=True))
    ).annotate(
        # And we want two fields available to the table in the end
        postcode=models.F('default_address__postcode'),
        line1=models.F('default_address__line1'),
    )

    def get_table_pagination(self, table) -> bool:
        # prevent getting and counting a complete queryset if we don't display the results
        return bool(self.request.GET)

    def get_table_kwargs(self) -> dict:
        # Dynamically hide columns based on search criteria & permissions
        visibility = {
            'email_address': self.request.GET.get('email'),
            'phone_number': self.request.GET.get('phone'),
            'student': self.request.user.has_perm('student.merge_student'),
        }
        return {'exclude': [column for column, visible in visibility.items() if not visible]}

    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        ids: list[str] = request.POST.getlist('student')
        int_ids: list[int] = [int(i) for i in ids if i.isnumeric()]
        if not Student.objects.filter(id__in=int_ids).exists():
            messages.error(request, 'No students selected')
            return redirect(request.get_full_path())
        url = reverse('student:merge') + '?' + urlencode({'student': int_ids}, doseq=True)
        return redirect(url)


class Lookup(LoginRequiredMixin, generic.View):
    """Redirects to a student record matching the husid or sits_id
    When not found, sends the user back to /search
    """

    def post(self, request) -> http.HttpResponse:
        husid = request.POST.get('husid', '')
        sits_id = request.POST.get('sits_id', '')
        try:
            if husid.isdigit():
                student = Student.objects.get(husid=husid)
            elif sits_id.isdigit():
                student = Student.objects.get(sits_id=sits_id)
            else:
                raise Student.DoesNotExist
            return redirect(student)
        except Student.DoesNotExist:
            messages.error(request, 'Student not found')
            return redirect('student:search')


class View(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    queryset = Student.objects.select_related(
        'nationality',
        'domicile',
        'diet',
        'disability',
        'ethnicity',
    )
    template_name = 'student/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_applications = self.object.course_applications.select_related('module').all()
        addresses = self.object.addresses.order_by('-is_default', '-is_billing', 'type', '-modified_on')
        emails = self.object.emails.order_by('-is_default', '-modified_on')
        enquiries = self.object.enquiries.select_related('module').order_by('-date')
        last_merger = StudentArchive.objects.filter(target=self.object.id).last()
        phones = self.object.phones.order_by('-is_default', '-modified_on')
        waitlists = self.object.waitlists.select_related('module').all()
        website_accounts = self.object.website_accounts.all()
        other_ids = self.object.other_ids.all()
        suspension = self.object.suspensions.order_by('-start_date')
        invoices = self.object.get_invoices()
        emergency_contact = getattr(self.object, 'emergency_contact', None)
        diet = getattr(self.object, 'diet', None)
        moodle_id = getattr(self.object, 'moodle_id', None)
        tutor = Tutor.objects.filter(student=self.object.id).prefetch_related('tutorsubjects').first()
        tutor_activities = tutor_modules = tutor_roles = tutor_modules_query = None

        tutor_module_role = self.request.GET.get('tutor_role', '')
        if tutor:
            tutor_activities = tutor.tutor_activities.select_related('activity').order_by('-id')
            # todo: annotate in the enrolment count, to avoid n+1
            tutor_modules = tutor.tutor_modules.select_related('module').order_by('-module__start_date')
            tutor_roles = tutor.tutor_modules.values_list('role', flat=True).exclude(role=None).distinct()
            tutor_modules_query = (
                # Todo: annotate enrolment count for the table
                tutor.tutor_modules.select_related('module')
                .prefetch_related('contracts')
                .order_by('-module__start_date')
            )
            if tutor_module_role:
                tutor_modules_query &= tutor_modules_query.filter(role__contains=tutor_module_role)

        qa_list = self.object.qualification_aims.select_related(
            'programme', 'programme__qualification'
        ).prefetch_related(
            Prefetch(
                'enrolments',
                queryset=Enrolment.objects.select_related('module', 'status').order_by(
                    '-module__start_date', 'module__code'
                ),
            )
        )
        qa_list.total_enrolments = sum(qa.enrolments.count() for qa in qa_list)
        qa_list.qa_certhe = any(qa.programme.is_certhe for qa in qa_list)

        for qa in qa_list:
            if qa.programme.qualification.id == 1:
                qa.non_accredited = True
                qa.qa_warning = any(enrolment.module.credit_points for enrolment in qa.enrolments.all())

            qa.points_awarded = sum(enrolment.points_awarded or 0 for enrolment in qa.enrolments.all())

        return {
            'addresses': addresses,
            'course_applications': course_applications,
            'emails': emails,
            'enquiries': enquiries,
            'diet': diet,
            'invoices': invoices,
            'last_merger': last_merger,
            'emergency_contact': emergency_contact,
            'phones': phones,
            'waitlists': waitlists,
            'website_accounts': website_accounts,
            'moodle_id': moodle_id,
            'other_ids': other_ids,
            'qa_list': qa_list,
            'suspension': suspension,
            'tutor': tutor,
            'tutor_activities': tutor_activities,
            'tutor_modules': tutor_modules,
            'tutor_roles': tutor_roles,
            'tutor_modules_query': tutor_modules_query,
            'tutor_module_role': tutor_module_role,
            **context,
        }


class Edit(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.UpdateView):
    model = Student
    template_name = 'core/form.html'
    form_class = forms.EditForm
    success_message = 'Record updated'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {'user': self.request.user, **kwargs}


class Delete(LoginRequiredMixin, PageTitleMixin, DeletionFailedMessageMixin, generic.DeleteView):
    model = Student
    template_name = 'core/delete_form.html'
    success_url = reverse_lazy('student:search')


class MakeTutor(LoginRequiredMixin, generic.View):
    """Converts a person into a tutor record"""

    http_method_names = ['get']

    # todo: convert to post once we have a good approach to post links
    def get(self, request, student_id):
        student = get_object_or_404(
            Student.objects.filter(tutor__id__isnull=True),  # Prevents attempting to create extra tutor records
            pk=student_id,
        )
        tutor = Tutor.objects.create(
            student=student, created_by=request.user.username, modified_by=request.user.username
        )
        messages.success(request, 'Tutor record created')
        return redirect(tutor.get_edit_url())


class Merge(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    permission_required = 'student.merge_student'
    template_name = 'student/merge.html'
    form_class = forms.MergeForm
    title = 'Person'
    subtitle = 'Merge'

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        record_ids = [int(i) for i in self.request.GET.getlist('student') if i.isnumeric()]
        return {**kwargs, 'record_ids': record_ids}

    def form_valid(self, form) -> http.HttpResponse:
        records = form.cleaned_data['records']
        try:
            target = services.merge.merge_multiple_students(records)
        except services.merge.CannotMergeError as e:
            form.add_error('records', e)
            return self.form_invalid(form)

        messages.success(self.request, f'{len(records)-1} records merged into {target}')
        return redirect(target)


# --- Email views ---


class CreateEmail(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.CreateView):
    form_class = forms.CreateEmailForm
    success_message = "Email address added: %(email)s"
    template_name = 'core/form.html'
    title = 'Email'

    def get_initial(self) -> dict:
        return {'student': get_object_or_404(Student, pk=self.kwargs['student_id'])}

    def get_success_url(self) -> str:
        return self.object.student.get_absolute_url() + '#email'


class EditEmail(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.UpdateView):
    model = Email
    template_name = 'core/form.html'
    form_class = forms.EmailForm
    success_message = "Email updated: %(email)s"

    def get_subtitle(self) -> str:
        return f'Edit – {self.object.email}'


class DeleteEmail(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = Email
    template_name = 'core/delete_form.html'

    def get_subtitle(self) -> str:
        return f'Delete – {self.object.email}'

    def get_success_url(self) -> str:
        messages.success(self.request, 'Email deleted')
        return self.object.student.get_absolute_url()


# --- Address views ---


class CreateAddress(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.CreateView):
    model = Address
    template_name = 'core/form.html'
    form_class = forms.AddressForm
    success_message = "Address added"

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form) -> http.HttpResponse:
        form.instance.student = self.student
        return super().form_valid(form)


class EditAddress(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.UpdateView):
    model = Address
    template_name = 'student/edit_address.html'
    form_class = forms.AddressForm
    success_message = "Address updated"


class DeleteAddress(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = Address
    template_name = 'core/delete_form.html'

    def get_success_url(self) -> str:
        messages.success(self.request, 'Address deleted')
        return self.object.student.get_absolute_url()


# --- Phone views ---


class CreatePhone(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.CreateView):
    form_class = forms.CreatePhoneForm
    success_message = "Phone number added: %(number)s"
    template_name = 'core/form.html'
    title = 'Phone'

    def get_initial(self) -> dict:
        return {'student': get_object_or_404(Student, pk=self.kwargs['student_id'])}

    def get_success_url(self) -> str:
        return self.object.student.get_absolute_url() + '#phone'


class EditPhone(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.UpdateView):
    model = Phone
    template_name = 'core/form.html'
    form_class = forms.PhoneForm
    success_message = 'Phone number updated: %(number)s'

    def get_subtitle(self) -> str:
        return f'Edit – {self.object.number}'


class DeletePhone(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = Phone
    template_name = 'core/delete_form.html'

    def get_subtitle(self) -> str:
        return f'Delete – {self.object.number}'

    def get_success_url(self) -> str:
        messages.success(self.request, 'Phone deleted')
        return self.object.student.get_absolute_url()


# --- Other ID views ---


class CreateOtherID(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.CreateView):
    form_class = forms.CreateOtherIDForm
    template_name = 'core/form.html'
    title = 'Other ID'
    success_message = 'Other ID added'

    def get_initial(self) -> dict:
        return {'student': get_object_or_404(Student, pk=self.kwargs['student_id'])}

    def get_success_url(self) -> str:
        return self.object.student.get_absolute_url() + '#other_ids'


class EditOtherID(LoginRequiredMixin, PageTitleMixin, AutoTimestampMixin, SuccessMessageMixin, generic.UpdateView):
    model = OtherID
    template_name = 'core/form.html'
    form_class = forms.OtherIDForm
    title = 'Other ID'
    success_message = 'Other ID updated'


class DeleteOtherID(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = OtherID
    template_name = 'core/delete_form.html'

    def get_subtitle(self) -> str:
        return f'Delete – {self.object.number}'

    def get_success_url(self) -> str:
        messages.success(self.request, 'Other ID deleted')
        return self.object.student.get_absolute_url()


# --- Moodle views ---


class CreateMoodleID(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.CreateView):
    model = MoodleID
    form_class = forms.CreateMoodleIDForm
    template_name = 'core/form.html'

    def get_initial(self) -> dict:
        return {'student': get_object_or_404(Student, pk=self.kwargs['student_id'])}

    def get_success_url(self) -> str:
        return self.object.student.get_absolute_url() + '#other_ids'


class EditMoodleID(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, generic.UpdateView):
    model = MoodleID
    template_name = 'core/form.html'
    form_class = forms.MoodleIDForm


class DeleteMoodleID(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = MoodleID
    template_name = 'core/delete_form.html'

    def get_subtitle(self) -> str:
        return f'Delete – {self.object.moodle_id}'

    def get_success_url(self) -> str:
        messages.success(self.request, 'Moodle ID deleted')
        return self.object.student.get_absolute_url() + '#other_ids'


# --- Emergency contact views ---


class CreateOrEditEmergencyContact(
    LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.UpdateView
):
    model = EmergencyContact
    form_class = forms.EmergencyContactForm
    template_name = 'core/form.html'
    success_message = 'Emergency contact details updated'
    subtitle_object = False

    def get_object(self, queryset=None):
        student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        obj, created = EmergencyContact.objects.get_or_create(
            student=student,
            defaults={'created_by': self.request.user.username, 'modified_by': self.request.user.username},
        )
        return obj

    def get_success_url(self):
        return self.object.student.get_absolute_url()


class DeleteEmergencyContact(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = EmergencyContact
    template_name = 'core/delete_form.html'

    def get_subtitle(self) -> str:
        return f'Delete – {self.object.name}'

    def get_success_url(self) -> str:
        messages.success(self.request, 'Emergency contact details deleted')
        return self.object.student.get_absolute_url()


# --- Other child views ---


class DeleteEnquiry(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = Enquiry
    template_name = 'core/delete_form.html'
    subtitle_object = False

    def get_success_url(self) -> str:
        messages.success(self.request, 'Enquiry deleted')
        return self.object.student.get_absolute_url() + '#enquiries'


class CreateOrEditDiet(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, generic.UpdateView):
    model = Diet
    fields = ['type', 'note']
    template_name = 'core/form.html'
    success_message = 'Dietary preferences updated'
    subtitle_object = False

    def get_object(self, queryset=None):
        student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        obj, created = Diet.objects.get_or_create(student=student)
        return obj

    def get_success_url(self):
        return self.object.student.get_absolute_url()


class StatementPDF(LoginRequiredMixin, generic.View):
    """Generate a statement for all a student's enrolments"""

    def get(self, request, pk: int, *args, **kwargs) -> http.HttpResponse:
        student = get_object_or_404(Student, pk=pk)
        document = pdfs.create_statement(student)
        filename = strings.normalize(f'Statement_{student.firstname}_{student.surname}.pdf')
        return http.HttpResponse(
            document, content_type='application/pdf', headers={'Content-Disposition': f'inline;filename={filename}'}
        )
