from django.urls import path
from django.views.defaults import page_not_found
from . import views

def index(request, i=3):
    from django.http import HttpResponse
    return HttpResponse(i)

app_name = 'programme'
urlpatterns = [
    path('view', views.view, {'id': 270}),
    path('search', views.Search.as_view(), name='search'),
    #path('view/<int:programme_id>', views.view, name='view'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('add-module/<int:programme_id>', page_not_found, name='add-module'),
]
