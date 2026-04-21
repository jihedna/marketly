from django.urls import path

from . import views

urlpatterns = [
    path("", views.ChatbotHomeView.as_view(), name="home"),
    path("new/", views.new_conversation, name="new"),
    path("send/", views.send_message, name="send"),
    path("c/<int:conv_id>/", views.ChatbotHomeView.as_view(), name="conversation"),
]
