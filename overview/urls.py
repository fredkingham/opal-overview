"""
Urls for the overview Opal plugin
"""
from django.conf.urls import url

from overview import views

urlpatterns = [
    url(
        '^overview/list$',
        views.OverviewListView.as_view(),
        name="overview_list"
    ),
    url(
        '^overview/subrecord/(?P<api_name>[0-9a-z_\-]+)?$',
        views.OverviewDetailView.as_view(),
        name="overview_detail_view"
    ),
]
