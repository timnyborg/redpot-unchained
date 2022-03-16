from django_auth_ldap import backend

from django import http
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from apps.core.models import User
from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin

from . import forms


class EditProfile(
    PageTitleMixin, AutoTimestampMixin, SuccessMessageMixin, PermissionRequiredMixin, generic.UpdateView
):
    """Allows a member of staff to edit their own profile / preferences, and admins to edit anyone"""

    model = User
    form_class = forms.UserForm
    template_name = 'core/form.html'
    subtitle = 'Edit profile'
    subtitle_object = False
    success_message = 'Profile updated'

    def get_permission_required(self) -> list:
        if self.kwargs.get('pk'):
            return ['core.edit_user']
        return []

    def get_object(self, queryset=None) -> User:
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(User, pk=pk)
        return self.request.user


class New(PageTitleMixin, SuccessMessageMixin, PermissionRequiredMixin, generic.FormView):
    title = 'User'
    subtitle = 'New'
    permission_required = 'core.add_user'
    template_name = 'core/form.html'
    form_class = forms.CreateUserForm
    success_message = 'User created'

    def form_valid(self, form) -> http.HttpResponse:
        username = form.cleaned_data['username']
        # Try populating the user from ldap
        self.object = backend.LDAPBackend().populate_user(username)
        if not self.object:
            self.object = User.objects.create_user(username)
        self.object.created_by = self.request.user.username
        self.object.modified_by = self.request.user.username
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('user:edit', kwargs={'pk': self.object.pk})
