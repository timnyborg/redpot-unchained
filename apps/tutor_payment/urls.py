from django.urls import include, path

from . import views

app_name = 'tutor-payment'

quick_payments_patterns = (
    [
        path('extras/<int:pk>', views.Extras.as_view(), name='extras'),  # 'tutor-payment:quick:extras'
        path('syllabus/<int:pk>', views.AddSyllabusFee.as_view(), name='syllabus'),
        path('teaching/online/<int:pk>', views.OnlineTeaching.as_view(), name='online-teaching'),
        path('teaching/weekly/<int:pk>', views.WeeklyTeaching.as_view(), name='weekly-teaching'),
    ],
    'quick',
)

urlpatterns = [
    path('new/<int:tutor_module_id>', views.Create.as_view(), name='new'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('export/', views.Export.as_view(), name='export'),
    path('transfer/', views.Transfer.as_view(), name='transfer'),
    path('quick/', include(quick_payments_patterns)),
    path('search/', views.Search.as_view(), name='search'),
    path('approve/', views.Approve.as_view(), name='approve'),
]
