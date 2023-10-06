from django.urls import path
from notifications import views

urlpatterns = [
    path('get/', views.notifications_get, name='notifications_get')
]