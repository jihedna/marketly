from django.urls import path

from . import dashboard_views as views

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),
]
