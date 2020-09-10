# -*- coding:utf-8 -*-
from django.urls import path
from . import views


app_name = 'loginapp'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('check_code/', views.check_code, name='check_code'),
    path('confirm/', views.user_confirm, name='confirm'),
]
