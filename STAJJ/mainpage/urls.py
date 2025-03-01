from django.urls import path
from . import views

urlpatterns = [
    path("", views.mainmenu, name="mainpage-mainmenu"),
    path("login/", views.login, name ="login"),
]
