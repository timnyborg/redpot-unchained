from django.urls import path

from . import views

app_name = 'feedback'
urlpatterns = [
    path('', views.ResultListView.as_view(), name='home'),
    path('results', views.ResultListView.as_view(), name='results'),
    path('results/year/<int:year>', views.ResultYearListView.as_view(), name='results-year'),
    path('results/this_week', views.ResultWeekListView.as_view(), name='results-last-week'),
    path('results/module/<str:code>', views.ResultModuleListView.as_view(), name='results-module'),
    path('previewquestions', views.PreviewQuestionnaireFormView.as_view(), name='previewquestions'),
    path('feedback_request', views.FeedbackRequestFormView.as_view(), name='feedbackrequest'),
    path('submit/<int:module_id>', views.ResultListView.as_view(), name='submit'),
    path('preview/<int:module_id>', views.PreviewView.as_view(), name='preview'),
    path('request_feedback/<int:module_id>', views.RequestFeedback.as_view(), name='request-feedback'),
    path('recently-completed', views.RecentlyCompletedOrFinishingSoon.as_view(), name='recently-completed'),
    path('export/xls/<int:module_id>', views.ExportToExcel.as_view(), name='export_users_xls'),
    path('make_pdf/<int:module_id>', views.make_pdf, name='make_pdf'),
]
