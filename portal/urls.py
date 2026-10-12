from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('booking/<int:showtime_id>/', views.book_seats, name='book_seats'),
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]
