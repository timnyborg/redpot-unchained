from rest_framework.routers import DefaultRouter

from django.urls import include, path

from . import api, views

app_name = 'proposal'

router = DefaultRouter()
router.register(r'', api.ProposalViewSet, basename='proposal')  # creates url names like proposal:api:proposal-reset

urlpatterns = [
    path('new', views.New.as_view(), name='new'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('search', views.Search.as_view(), name='search'),
    # api
    path('api/', include((router.urls, 'api'))),
]
