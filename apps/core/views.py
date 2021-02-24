from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm


# A custom Login form & view to enable overriding error_messages
class CustomAuthForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Please enter your departmental %(username)s and password",
        'inactive': "This account is inactive."
    }


class CustomLoginView(LoginView):
    authentication_form = CustomAuthForm


def index(request):
    return render(request, 'index.html')
