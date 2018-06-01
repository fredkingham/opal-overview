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
]
