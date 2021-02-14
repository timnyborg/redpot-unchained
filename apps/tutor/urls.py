from django.urls import path, include
from django.views.defaults import page_not_found
from . import views

app_name = 'tutor'

tutor_module_patterns = ([
    path('view/<int:pk>', views.TutorOnModuleView.as_view(), name='view'),  # tutor:module:view
], 'module')

urlpatterns = [
    path('tutor-module/', include(tutor_module_patterns)),
    # Todo: overhaul this whole expense-form url structure
    path('expense-form/module/<int:pk>/<str:template>', views.ExpenseFormView.as_view(), {'mode': 'module'}, name='expense-form-module'),
    path('expense-form/record/<int:pk>/<str:template>', views.ExpenseFormView.as_view(), {'mode': 'single'}, name='expense-form-single'),
    path('expense-form/pattern/<str:template>', views.ExpenseFormView.as_view(), {'mode': 'search'}, name='expense-form-pattern'),
]
