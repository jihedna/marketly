from django.urls import path

from . import views

urlpatterns = [
    path("", views.ServicesListView.as_view(), name="list"),
]
