from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('404/', views.NotFound404, name='404'),
    path('movie/<movie_id>/', views.movie, name='movie'),
    path('movie/<movie_id>/favourite/', views.favourite, name='favourite'),
    path('movie/<movie_id>/log/', views.log, name='log'),
    path('movie/<movie_id>/add/', views.add_to_list, name='add_to_list'),
    path('movie/<movie_id>/gapt/', views.createGapt, name='create_gapt'),
    path('person/<person_id>/', views.person, name='person'),
    path('list/new/', views.newList, name='new_list'),
    path('list/<list_id>/', views.userList, name='list'),
    path('gapt/like/', views.likeGapt, name='like_gapt'),
    path('gapt/seen/', views.markGaptAsSeen, name='like_gapt'),
    path('gapt/reGapt/', views.reGapt, name='like_gapt'),
    path('search/', views.search, name='search'),
    path('searchFilms/', views.search_films, name='search_films'),
]
