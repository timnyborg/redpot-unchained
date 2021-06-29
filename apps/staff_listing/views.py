from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.utils.views import PageTitleMixin
from apps.core.models import User
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
    model = User
    template_name = 'staff_listing/profile.html'
    context_object_name = 'staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class WallListView(LoginRequiredMixin, PageTitleMixin, ListView):
    model = User
    title = 'Staff listing'
    subtitle = 'Wall'
    template_name = 'staff_listing/wall.html'
    context_object_name = 'staffs'


# def list():
#     user = idb.auth_user
#     profiles = idb(
#         (user.is_active == True)
#         & (user.division == idb.division.id)
#     ).select(
#         user.id.with_alias('id'),
#         user.first_name.with_alias('first_name'),
#         user.last_name.with_alias('last_name'),
#         user.email.with_alias('email'),
#         user.phone.with_alias('phone'),
#         user.role.with_alias('role'),
#         idb.division.name.with_alias('division'),
#     )
#     return dict(profiles=profiles)
#
#
# def courses():
#     manager = idb.auth_user.with_alias('manager')
#     staff = idb.auth_user.with_alias('staff')
#
#     programmes = idb(
#         (idb.programme.division == idb.division.id)
#         & (idb.programme.contact_list_display == True)
#     ).select(
#         manager.ALL,
#         staff.ALL,
#         idb.programme.ALL,
#         idb.staff_role.ALL,
#         idb.programme_staff.note,
#         left=[
#             manager.on(idb.division.manager == manager.id),
#             idb.programme_staff.on(idb.programme_staff.programme == idb.programme.id),
#             staff.on(idb.programme_staff.staff == staff.id),
#             idb.staff_role.on(idb.programme_staff.role == idb.staff_role.id)
#         ],
#         orderby=[
#             idb.programme.short_name.coalesce(idb.programme.title),
#             idb.programme_staff.role,
#             idb.staff.last_name,
#             idb.staff.first_name
#         ]
#     )
#
#     structure = [
#         ('Non-accredited', 'non-acc', {1}),
#         ('Undergraduate short courses', 'ug-credit', {61}),
#         ('Undergraduate certificates', 'ug-cert', {30, 33}),
#         ('Undergraduate diplomas', 'ug-dip', {34, 35}),
#         ('Postgraduate short courses', 'pg-credit', {62, 63}),
#         ('Postgraduate certificates', 'pg-cert', {6}),
#         ('Postgraduate diplomas', 'pg-dip', {7}),
#         ('Masters degrees', 'masters', {5}),
#         ('D.Phils', 'dphils', {2, 3}),
#     ]
#
#     return dict(programmes=programmes, structure=structure)
