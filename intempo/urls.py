from django.urls import path
from intempo import views

app_name = "intempo"

urlpatterns = [
    path("home/", views.index, name="home"),
    path("albums/", views.albums, name="albums"),
    path("albums/album_name/", views.album_page, name="album_page"),
    path("albums/add_album", views.add_album, name="add_album"),
    path("user/user_name/", views.profile, name="profile"),
    path("sign-up/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("404/", views.not_found, name="not_found")
]
