from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import add_event
urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name='users/login.html'), name = "login"),
    path("logout/", auth_views.LogoutView.as_view(template_name='users/logout.html'), name = "logout"),
    path('event/<int:event_id>/add_event/',add_event,name='added event to user'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'), name='password_reset_complete'),  
]