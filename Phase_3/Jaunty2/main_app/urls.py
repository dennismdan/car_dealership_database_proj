from django.urls import path

from . import views

'''
https://docs.djangoproject.com/en/3.2/topics/http/urls/
'''


urlpatterns = [
    path('', views.home, name="home"),
    path('home/', views.home, name="home"),
    path('reports/', views.reports, name="reports"),
    path('login/', views.login, name="login"),
    path('loggedin/', views.loggedin, name="loggedin"),
    path('lookup_customer/', views.lookup_customer, name="lookup_customer"),
    path('filter_vehicles/', views.filter_vehicles, name="filter_vehicles"),
    path('add_customer/', views.add_customer, name="add_customer"),
    path('total_vehicles_available/', views.total_vehicles_available, name="total_vehicles_available"),
    path('individual/', views.update_add_customer, name="individual"),
    path('business/', views.update_add_customer, name="business"),
    path('vehicle_details/<str:vin>/', views.vehicle_details, name="vehicle_details"),
    path('add_repair/', views.add_repair, name="add_repair"),
    path('sell_vehicle/<str:vin>/', views.sell_vehicle, name="sell_vehicle"),
    path('update_vehicle_type/', views.update_vehicle_type, name="update_vehicle_type"),
    path('repairs/', views.repairs, name="repairs"),
    path('add_vehicle/', views.add_vehicle, name="add_vehicle"),
    path('monthlysales_drilldown/<int:year>/<int:month>/', views.monthlysales_drilldown, name="monthlysales_drilldown")

    path('add_repair/', views.add_repair, name="add_repair"),
    path('update_repair/', views.update_repair, name="update_repair"),
    path('add_part/', views.add_part, name="add_part")
]
