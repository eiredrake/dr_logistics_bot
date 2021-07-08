from django.conf.urls import url
from django.urls import path, include
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


app_name='logistics'
urlpatterns = [
    path('register', views.register_request, name='register'),
    path('login', views.login_request, name='login'),
    path('logout', views.logout_request, name='logout'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='logistics/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="logistics/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='logistics/password_reset_complete.html'),
         name='password_reset_complete'),
    path("password_reset", views.password_reset_request, name="password_reset")
]
