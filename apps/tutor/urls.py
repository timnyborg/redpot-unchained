from django.urls import include, path

from . import api, views

app_name = 'tutor'

tutor_module_patterns = (
    [
        path('delete/<int:pk>', views.TutorOnModuleDelete.as_view(), name='delete'),  # tutor:module:delete
        path('edit/<int:pk>', views.TutorOnModuleEdit.as_view(), name='edit'),  # tutor:module:edit
        path('new/', views.TutorOnModuleCreate.as_view(), name='new'),  # tutor:module:new
        path('view/<int:pk>', views.TutorOnModuleView.as_view(), name='view'),  # tutor:module:view
        # apis
        path('reorder', api.ReorderAPI.as_view(), name='reorder'),
    ],
    'module',
)

activity_patterns = (
    [
        path('new/<int:tutor_id>', views.CreateTutorActivity.as_view(), name='new'),  # tutor:activity:new
        path('edit/<int:pk>', views.EditTutorActivity.as_view(), name='edit'),
        path('delete/<int:pk>', views.DeleteTutorActivity.as_view(), name='delete'),
    ],
    'activity',
)

urlpatterns = [
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),  # tutor:edit
    path('right-to-work/<int:pk>', views.RightToWork.as_view(), name='right-to-work'),
    path('tutor-module/', include(tutor_module_patterns)),
    path('activity/', include(activity_patterns)),
    # Todo: overhaul this whole expense-form url structure
    path(
        'expense-form/module/<int:pk>/<str:template>',
        views.ExpenseFormView.as_view(),
        {'mode': 'module'},
        name='expense-form-module',
    ),
    path(
        'expense-form/record/<int:pk>/<str:template>',
        views.ExpenseFormView.as_view(),
        {'mode': 'single'},
        name='expense-form-single',
    ),
    path(
        'expense-form/pattern/<str:template>',
        views.ExpenseFormView.as_view(),
        {'mode': 'search'},
        name='expense-form-pattern',
    ),
]
