from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.utils.views import PageTitleMixin
# from apps.core.models import User
from .models import ProgrammeStaff, Programme, User, Division, StaffRole
from django_tables2 import SingleTableView
from .datatables import StaffListTable
from django.views.generic import ListView, DetailView

def wall(request):
    return render(request, 'staff_listing/wall.html')

def index(request):
    return HttpResponse("Yo! from index")

def list(request):
    return HttpResponse("Hi, from list")

def courses(request):
    return HttpResponse("Hiya, from courses...")

# reference from web2py
# def wall():
#     profiles = idb(
#         (idb.auth_user.is_active == True)
#         & (idb.auth_user.on_facewall == True)
#     ).select(idb.auth_user.ALL)
#     # User table -> Get all cols, Filter by is_active & on_facewall == True
#     return dict(profiles=profiles)

class StaffListView(LoginRequiredMixin, PageTitleMixin, SingleTableView):
    title = 'Staff listing'
    subtitle = 'List'
    template_name = 'staff_listing/list.html'
    # model = User
    table_class = StaffListTable
    table_pagination = False

    def get_queryset(self):
        return User.objects.filter()
        # return User.objects.filter(is_active = 1)

class StaffDetailView(LoginRequiredMixin, PageTitleMixin, DetailView):
    title = 'Staff listing'
    subtitle = 'Profile'
    model = User
    template_name = 'staff_listing/profile.html'
    context_object_name = 'staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['staff_programmes'] = ProgrammeStaff.objects.filter(staff=self.object.id)
        # print(context)
        context['staff_programmes'] = self.object.programme_staff_set.all()
        print(context)
        return context

class WallListView(LoginRequiredMixin, PageTitleMixin, ListView):
    # model = User
    title = 'Staff listing'
    subtitle = 'Wall'
    template_name = 'staff_listing/wall.html'
    context_object_name = 'staffs'

    def get_queryset(self):
        return User.objects.filter()
        # return User.objects.filter(is_active=1, on_facewall=1)

class CoursesListView(LoginRequiredMixin, PageTitleMixin, ListView):
    title = 'Staff listing'
    subtitle = 'Courses list'
    template_name = 'staff_listing/courses_list.html'
    # model = Programme
    context_object_name = 'programmes'

    def get_queryset(self):
        progs = Programme.objects.filter(contact_list_display=1)
        return progs

    # Tables needed:
    # programme -> title, phone, email
    # programme_staff -> joins user
    # division -> joins manager
    # core_user -> first_name, last_name
    # staff_role -> 'name'
    def get_context_data(self, **kwargs):
        context = super(CoursesListView, self).get_context_data(**kwargs)
        context['non-acc'] = [('Non-accredited', 'non-acc', self.object_list.filter(qualification=1))]
        context['ug-credit'] = [('Undergraduate short courses', 'ug-credit', self.object_list.filter(qualification=61))]
        context['ug-cert'] = [('Undergraduate certificates', 'ug-cert', self.object_list.filter(qualification__in=[30,33]))]
        context['ug-dip'] = [('Undergraduate diplomas', 'ug-dip', self.object_list.filter(qualification__in=[34,35]))]
        context['pg-credit'] = [('Postgraduate short courses', 'pg-credit', self.object_list.filter(qualification__in=[62,63]))]
        context['pg-cert'] = [('Postgraduate certificates', 'pg-cert', self.object_list.filter(qualification=6))]
        context['pg-dip'] = [('Postgraduate diplomas', 'pg-dip', self.object_list.filter(qualification=7))]
        context['masters'] = [('Masters degrees', 'masters', self.object_list.filter(qualification=5))]
        context['dphils'] = [('D.Phils', 'dphils', self.object_list.filter(qualification__in=[2,3]))]

        context['structure'] = [('Non-accredited', 'non-acc', self.object_list.filter(qualification=1)),
                                ('Undergraduate short courses', 'ug-credit', self.object_list.filter(qualification=61)),
                                ('Undergraduate certificates', 'ug-cert', self.object_list.filter(qualification__in=[30, 33])),
                                ('Undergraduate diplomas', 'ug-dip', self.object_list.filter(qualification__in=[34, 35])),
                                ('Postgraduate short courses', 'pg-credit', self.object_list.filter(qualification__in=[62, 63])),
                                ('Postgraduate certificates', 'pg-cert', self.object_list.filter(qualification=6)),
                                ('Postgraduate diplomas', 'pg-dip', self.object_list.filter(qualification=7)),
                                ('Masters degrees', 'masters', self.object_list.filter(qualification=5)),
                                ('D.Phils', 'dphils', self.object_list.filter(qualification__in=[2, 3]))
                               ]

        print(context)
        return context
