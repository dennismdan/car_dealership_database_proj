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
    path('sell_vehicle/<str:vin>/', views.sell_vehicle, name="sell_vehicle"),
    path('update_vehicle_type/', views.update_vehicle_type, name="update_vehicle_type"),
    path('add_vehicle/', views.add_vehicle, name="add_vehicle"),
    path('repairs/', views.repairs, name="repairs"),
    path('monthlysales_drilldown/<int:year>/<int:month>/', views.monthlysales_drilldown, name="monthlysales_drilldown"),
    path('add_repair/', views.add_repair, name="add_repair"),
    path('edit_repair/<str:VIN>/<int:Customer_id>/<str:Start_date>/', views.edit_repair, name="edit_repair"),
    path('close_repair/<str:VIN>/<int:Customer_id>/<str:Start_date>/', views.close_repair, name="close_repair"),
    path('add_part/<str:VIN>/<int:Customer_id>/<str:Start_date>/', views.add_part, name="add_part"),
    path('view_part/<str:VIN>/<int:Customer_id>/<str:Start_date>/', views.view_part, name="view_part"),
    path('gross_customer_income_drilldown/<int:Customer_id>/',
         views.gross_customer_income_drilldown,
         name="gross_customer_income_drilldown"),
    path('repairsby_manu_type_model_drill/<str:manufacturer_name>/',
         views.repairsby_manu_type_model_drill,
         name="repairsby_manu_type_model_drill"),

]
