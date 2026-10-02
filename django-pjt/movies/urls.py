from django.urls import path
from . import views


urlpatterns = [
    path('genres/', views.genre_list),
    path('movies/', views.movie_list),
    path('movies/recommend/', views.movie_recommend),
    path('movies/<int:movie_pk>/', views.movie_detail),
    path('movies/<int:movie_pk>/reviews/', views.review_create),
    path('reviews/', views.review_list),
    path('reviews/<int:review_pk>/', views.review_detail),
]
