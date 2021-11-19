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
<<<<<<< HEAD
    path('loggedin/', views.loggedin, name="loggedin"),
    path('lookup_customer/', views.lookup_customer, name="lookup_customer"),
=======
    path('add_customer/', views.add_customer, name="add_customer")

>>>>>>> 22521a8d10571bcd03a00152e9716b802daf8036
]
