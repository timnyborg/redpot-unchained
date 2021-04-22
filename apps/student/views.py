from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.shortcuts import get_object_or_404
from django.views import generic
from django.shortcuts import render

from apps.core.utils.views import PageTitleMixin

from . import datatables, forms
from .models import Student
from .forms import StudentSearchForm


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

    def get_initial(self):
        return {'student': get_object_or_404(Student, pk=self.kwargs['student_id'])}

    def get_success_url(self):
        return self.object.student.get_absolute_url() + '#email'


def searchStudent(request):
    form = StudentSearchForm()
    students = Student.objects.all()
    return render(request, "student/search.html",
                  {"form": form, "students": students})
