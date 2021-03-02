from django.urls import path
from intempo import views

app_name = "intempo"

urlpatterns = [
    path("home/", views.index, name="home"),
]
