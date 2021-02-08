from django.urls import path
from django.views.defaults import page_not_found
from . import views

app_name = 'tutor'
urlpatterns = [
    # Todo: overhaul this whole expense-form url structure
    path('expense-form/module/<int:pk>/<str:template>', views.ExpenseFormView.as_view(), {'mode': 'module'}, name='expense-form-module'),
    path('expense-form/record/<int:pk>/<str:template>', views.expense_form, {'mode': 'single'}, name='expense-form-single'),
    path('expense-form/pattern/<str:template>', views.expense_form, name='expense-form-search'),
]
