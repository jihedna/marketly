from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("set-theme/", views.set_theme, name="set_theme"),
    path("set-language/", views.set_language_pref, name="set_language"),
]
