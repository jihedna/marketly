from django.urls import path

from . import views

urlpatterns = [
    path("", views.SolutionsListView.as_view(), name="list"),
    path("plan/<int:pk>/", views.StrategyPlanDetailView.as_view(), name="plan_detail"),
    path("<slug:slug>/", views.SolutionDetailView.as_view(), name="detail"),
    path("<slug:slug>/start/", views.StartSolutionView.as_view(), name="start"),
]
