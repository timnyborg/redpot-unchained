from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from apps.main.forms import PageTitleMixin

from apps.main.models import User


class EditProfile(PageTitleMixin, SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """View allowing a member of staff to edit their own profile / preferences"""
    model = User
    fields = ('first_name', 'last_name', 'role', 'phone', 'room', 'image')
    template_name = 'user/edit.html'
    subtitle = 'Edit profile'
    subtitle_object = False
    success_message = 'Profile updated'
    success_url = '/'

    def get_object(self, queryset=None):
        return self.request.user
