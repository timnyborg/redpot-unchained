from django.urls import path

from . import api, views

app_name = 'module'

urlpatterns = [
    path('clone/<int:pk>', views.Clone.as_view(), name='clone'),
    path('clone', views.Clone.as_view(), name='clone'),
    path('copy-fees/<int:module_id>', views.CopyFees.as_view(), name='copy-fees'),
    path('copy-web-fields/<int:module_id>', views.CopyWebFields.as_view(), name='copy-web-fields'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('new', views.New.as_view(), name='new'),
    path('search', views.Search.as_view(), name='search'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('cancel/<int:pk>', views.Cancel.as_view(), name='cancel'),
    path('uncancel/<int:pk>', views.Uncancel.as_view(), name='uncancel'),
    path('syllabus/<int:pk>', views.Syllabus.as_view(), name='syllabus'),
    path('award-points/<int:pk>', views.AwardPoints.as_view(), name='award-points'),
    path('award-points', views.AwardPoints.as_view(), name='award-points'),  # for get method
    path(
        'rebuild-recommended-reading/<int:pk>',
        views.RebuildRecommendedReading.as_view(),
        name='rebuild-recommended-reading',
    ),
    # child record views
    path('programme/add/<int:module_id>', views.AddProgramme.as_view(), name='add-programme'),
    path('payment-plan/add/<int:module_id>', views.AddPaymentPlan.as_view(), name='add-payment-plan'),
    path(
        'payment-plan/remove/<int:module_id>/<int:plan_type_id>',
        views.RemovePaymentPlan.as_view(),
        name='remove-payment-plan',
    ),
    path('hesa-subjects/edit/<int:pk>', views.EditHESASubjects.as_view(), name='edit-hesa-subjects'),
    path('book/add/<int:module_id>', views.AddBook.as_view(), name='add-book'),
    path('book/edit/<int:pk>', views.EditBook.as_view(), name='edit-book'),
    path('book/delete/<int:pk>', views.DeleteBook.as_view(), name='delete-book'),
    # reports
    path('student-list/<int:pk>', views.StudentList.as_view(), name='student-list'),
    path('moodle-list/<int:pk>', views.MoodleList.as_view(), name='moodle-list'),
    path('class-register/<int:pk>', views.ClassRegister.as_view(), name='class-register'),
    # apis
    path('update-api/<int:pk>', api.ModuleUpdateAPI.as_view(), name='update-api'),
]
