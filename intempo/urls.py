from django.urls import path
from intempo import views
from django.contrib.auth import views as auth_views

app_name = "intempo"

urlpatterns = [
    path("albums/", views.albums, name="albums"),
    path("albums/<int:album_id>/", views.album_page, name="album_page"),
    path("albums/add_album/", views.add_album, name="add_album"),
    path("albums/filter_by/<str:sort_type>/", views.sort_albums, name="sort_albums"),
    path("user/<str:username>/", views.profile, name="profile"),
    path("sign-up/", views.signup, name="signup"),
    path("albums/<int:album_id>/add_review/", views.add_review, name="add_review"),
    path("albums/<int:review_id>/add_comment/", views.add_comment, name="add_comment"),
    path("login/", auth_views.LoginView.as_view(template_name = 'intempo/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
