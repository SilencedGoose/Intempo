from django.urls import path
from intempo import views
from django.contrib.auth import views as auth_views

app_name = "intempo"

urlpatterns = [
    path("home/", views.index, name="home"),
    path("albums/", views.albums, name="albums"),
    path("albums/<int:album_id>/", views.album_page, name="album_page"),
    path("albums/add_album", views.add_album, name="add_album"),
    path("user/user_name/", views.profile, name="profile"),
    path("sign-up/", views.signup, name="signup"),
    path("404/", views.not_found, name="not_found"),
    path("albums/album_name/add_review", views.add_review, name="add_review"),
    path("login/", auth_views.LoginView.as_view(template_name = 'intempo/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
