from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('<convo_id>', views.chat_convo, name='chat_convo'),
]