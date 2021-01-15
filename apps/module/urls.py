from django.urls import path
from . import views

def index(request, i=3):
    from django.http import HttpResponse
    return HttpResponse(i)

app_name = 'module'
urlpatterns = [
    path('search', views.Search.as_view(), name='search'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
]
