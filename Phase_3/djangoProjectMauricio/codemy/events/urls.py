from django.urls import path

from events import views

urlpatterns = [
    # int:numbers
    # str:strings
    # path: whole urls
    # slug: hyphen and underscores stuff
    # UUID: universal identifier
    path('', views.home, name="home"),
    path('<int:year>/<str:month>/', views.home, name="home"),
    path('sql', views.run_query, name='show-sql'),
    path('events', views.all_events, name='list-events')


]



