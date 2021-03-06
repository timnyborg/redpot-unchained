from django.urls import path

from . import views

app_name = 'programme'
urlpatterns = [
    path('search', views.Search.as_view(), name='search'),
    path('new', views.New.as_view(), name='new'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('add-module/<int:programme_id>', views.AddModule.as_view(), name='add-module'),
    path('remove-module/<int:programme_id>/<int:module_id>', views.RemoveModule.as_view(), name='remove-module'),
]
