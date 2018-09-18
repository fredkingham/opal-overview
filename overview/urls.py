"""
Urls for the overview Opal plugin
"""
from django.conf.urls import url

from overview import views

urlpatterns = [
    url(
        '^overview/list$',
        views.OverviewSubrecordListView.as_view(),
        name="overview_list"
    ),
    url(
        '^overview/all/subrecord/(?P<api_name>[0-9a-z_\-]+)?$',
        views.OverviewDetailView.as_view(),
        name="overview_detail_view"
    ),
    url(
        '^overview/category/(?P<category>[0-9a-z_\-]+)?$/subrecord/(?P<api_name>[0-9a-z_\-]+)?$',
        views.OverviewDetailView.as_view(),
        name="overview_detail_view"
    ),
    url(
        '^overview/tagging/(?P<tagging>[0-9a-z_\-]+)?$/subrecord/(?P<api_name>[0-9a-z_\-]+)?$',
        views.OverviewDetailView.as_view(),
        name="overview_detail_view"
    ),
]
