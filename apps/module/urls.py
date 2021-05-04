from django.urls import include, path

from . import views

app_name = 'module'

fee_patterns = (
    [
        path('new/<int:module_id>', views.CreateFee.as_view(), name='new'),  # module:fee:new
        path('edit/<int:pk>', views.EditFee.as_view(), name='edit'),
    ],
    'fee',
)

urlpatterns = [
    path('clone/<int:pk>', views.Clone.as_view(), name='clone'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('new', views.New.as_view(), name='new'),
    path('search', views.Search.as_view(), name='search'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    # support functions
    path('toggle-auto-reminder/<int:pk>', views.toggle_auto_reminder, name='toggle-auto-reminder'),
    path('toggle-auto-feedback/<int:pk>', views.toggle_auto_feedback, name='toggle-auto-feedback'),
    path('fee/', include(fee_patterns)),
]
