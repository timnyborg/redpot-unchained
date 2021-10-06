from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import UpdateView

from apps.core.models import User
from apps.core.utils.views import PageTitleMixin


class EditProfile(PageTitleMixin, SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """View allowing a member of staff to edit their own profile / preferences"""

    model = User
    fields = ('first_name', 'last_name', 'email', 'role', 'phone', 'room', 'image')
    template_name = 'core/form.html'
    subtitle = 'Edit profile'
    subtitle_object = False
    success_message = 'Profile updated'
    success_url = '/'

    def get_object(self, queryset=None) -> User:
        return self.request.user

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()
