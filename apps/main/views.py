from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {'right_sidebar_enabled': False})