from django.urls import path
from . import views
from .views import (getAlbumArt, sendID)

urlpatterns = [
    path('', views.home),
    path('search', views.search),
    path('artist', views.artist),
    path('quiz', views.quiz),
    path('albums', views.album_search),
    path('get_album_art', getAlbumArt, name = "get_album_art"),
    path('post/ajax/send_id', sendID, name = "send_id")
]
