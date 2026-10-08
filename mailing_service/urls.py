from django.contrib import admin
from django.urls import path
from django.views.decorators.cache import cache_page

from .apps import MailingServiceConfig
from .views import (
    AboutView,
    DisableDistributionView,
    DistrbutionCreateView,
    DistributionListView,
    MainPageView,
    MessageCreateView,
    RecipientCreateView,
    StatisticsView,
    UserBlockView,
    UserListView,
)

app_name = MailingServiceConfig.name

urlpatterns = [
    path("", MainPageView.as_view(), name="main_page"),
    path(
        "distribution_create",
        DistrbutionCreateView.as_view(),
        name="distribution_create",
    ),
    path("distributions", DistributionListView.as_view(), name="distributions"),
    path("message_create/", MessageCreateView.as_view(), name="message_create"),
    path("recipient_create/", RecipientCreateView.as_view(), name="recipient_create"),
    path("statistics/", StatisticsView.as_view(), name="statistics"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/block/", UserBlockView.as_view(), name="user_block"),
    path(
        "distribution/<int:pk>/disable/",
        DisableDistributionView.as_view(),
        name="distribution_disable",
    ),
    path("about/", AboutView.as_view(), name="about"),
]
