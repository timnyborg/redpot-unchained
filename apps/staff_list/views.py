from django_tables2 import SingleTableView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from apps.core.utils.views import PageTitleMixin
from apps.programme.models import Programme

from .datatables import StaffListTable
from .models import User


class SiteTitleMixin(PageTitleMixin):
    title = 'Staff List'


class StaffListView(LoginRequiredMixin, SiteTitleMixin, SingleTableView):
    subtitle = 'Contact details'
    template_name = 'staff_list/list.html'
    table_class = StaffListTable
    table_pagination = False
    queryset = User.objects.filter(is_active=True)


class StaffDetailView(LoginRequiredMixin, SiteTitleMixin, DetailView):
    model = User
    template_name = 'staff_list/profile.html'
    context_object_name = 'staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff_programmes'] = self.object.programme_staff_set.all()
        return context

    def get_subtitle(self) -> str:
        return f'Profile – {self.object.get_full_name()}'


class WallListView(LoginRequiredMixin, SiteTitleMixin, ListView):
    subtitle = 'Wall'
    template_name = 'staff_list/wall.html'
    context_object_name = 'staffs'
    queryset = User.objects.filter(is_active=True, on_facewall=True).order_by('last_name', 'first_name')


class CoursesListView(LoginRequiredMixin, SiteTitleMixin, ListView):
    subtitle = 'Courses list'
    template_name = 'staff_list/courses_list.html'
    queryset = (
        Programme.objects.filter(contact_list_display=True)
        .select_related('division', 'division__manager')
        .prefetch_related('programme_staff_set', 'programme_staff_set__staff', 'programme_staff_set__role')
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qualifications'] = [
            ('Non-accredited', 'non-acc', self.object_list.filter(qualification=1)),
            ('Undergraduate short courses', 'ug-credit', self.object_list.filter(qualification=61)),
            ('Undergraduate certificates', 'ug-cert', self.object_list.filter(qualification__in=[30, 33])),
            ('Undergraduate diplomas', 'ug-dip', self.object_list.filter(qualification__in=[34, 35])),
            ('Postgraduate short courses', 'pg-credit', self.object_list.filter(qualification__in=[62, 63])),
            ('Postgraduate certificates', 'pg-cert', self.object_list.filter(qualification=6)),
            ('Postgraduate diplomas', 'pg-dip', self.object_list.filter(qualification=7)),
            ('Masters degrees', 'masters', self.object_list.filter(qualification=5)),
            ('D.Phils', 'dphils', self.object_list.filter(qualification__in=[2, 3])),
        ]
        return context
