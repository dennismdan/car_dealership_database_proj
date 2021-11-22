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
    path('loggedin/', views.loggedin, name="loggedin"),
    path('lookup_customer/', views.lookup_customer, name="lookup_customer"),
    path('filter_vehicles/', views.filter_vehicles, name="filter_vehicles"),
    path('add_customer/', views.add_customer, name="add_customer"),
    path('total_vehicles_available/', views.total_vehicles_available, name="total_vehicles_available"),
    path('individual/', views.individual, name="individual"),
    path('business/', views.business, name="business"),


]
