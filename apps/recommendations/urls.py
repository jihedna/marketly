from django.urls import path

from . import views

urlpatterns = [
    path("", views.RecommendationsView.as_view(), name="home"),
]
