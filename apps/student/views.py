from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.db.models import Q
from django.forms import Form
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from apps.core.utils.views import PageTitleMixin
from apps.tutor.models import Tutor

from . import datatables, forms
from .models import Email, Student


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
        )

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
            table = datatables.CreateMatchTable(data=queryset)
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
    template_name = 'core/search.html'

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

    def get_table_kwargs(self):
        # Can also be used for hiding the merge column based on permissions
        # Hide the email column unless we search by it
        exclude = []
        if not self.request.GET.get('email'):
            exclude.append('email_address')
        return {'exclude': exclude}


class CreateEmail(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, generic.CreateView):
    form_class = forms.CreateEmailForm
    success_message = "Email address added: %(email)s"
    template_name = 'core/form.html'
    title = 'Email'

    def get_initial(self) -> dict:
        return {'student': get_object_or_404(Student, pk=self.kwargs['student_id'])}

    def get_success_url(self) -> str:
        return self.object.student.get_absolute_url() + '#email'


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
