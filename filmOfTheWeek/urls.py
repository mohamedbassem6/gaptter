from django.urls import path
import filmOfTheWeek.views as views

urlpatterns = [
    path('', views.home, name=('film_of_the_week_home'))
]