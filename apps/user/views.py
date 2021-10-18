from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import UpdateView

from apps.core.models import User
from apps.core.utils.views import PageTitleMixin

from . import forms


class EditProfile(PageTitleMixin, SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """Allows a member of staff to edit their own profile / preferences"""

    model = User
    form_class = forms.UserForm
    template_name = 'core/form.html'
    subtitle = 'Edit profile'
    subtitle_object = False
    success_message = 'Profile updated'

    def get_object(self, queryset=None) -> User:
        return self.request.user
