from django.urls import include, path
from . import views
from users import views as user_views
from django import forms

urlpatterns = [
    path("login/", views.login, name ='login'),
    path("home/", views.home, name='cockycal-home'),
    path("profile/", views.profile, name='cockycal-profile'),
    path("tasklist/", views.ItemListView.as_view(), name='cockycal-tasklist'),
    path("login/", views.login, name ="cockycal-login"),
    # CRUD patterns for ToDoItems
    path(
        "tasklist/item/add/",
        views.ItemCreate.as_view(),
        name="item-add",
    ),
    path(
        "tasklist/item/<int:pk>/",
        views.ItemUpdate.as_view(),
        name="item-update",
    ),
    path(
        "tasklist/item/<int:pk>/delete/",
        views.ItemDelete.as_view(),
        name="item-delete",
    ),
    path("cal/",include('cal.urls',namespace='details')),
]
