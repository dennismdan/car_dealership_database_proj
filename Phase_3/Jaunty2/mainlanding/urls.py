from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('home/', views.home, name="home"),
    path('add_vehicle/', views.add_vehicle, name="add_vehicle"),
    path('reports/', views.reports, name="reports"),
    path('repairs/', views.repairs, name="repairs"),
    path('login/', views.login, name="login"),
    path('loggedin/', views.loggedin, name="loggedin"),
]