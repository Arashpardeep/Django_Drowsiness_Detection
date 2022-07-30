from django.contrib import admin
from django.urls import path
from home import views 

urlpatterns = [
    path("", views.signin, name = 'signin'),
    path("Signup", views.Signup, name = 'signup'),
    path("index", views.index, name = 'index'),
    path("statistics", views.statistics, name = 'statistics'),
    path("working", views.working, name = 'working'),
    path("signout", views.signout, name = 'signout'),
    # path("activate/<uid64>/<token>", views.activate, name = 'activate'),
    path("webcam", views.webcam, name = 'webcam'),
    path("profile", views.profile, name = 'profile')
]
