import pyodbc
from django.http import request
from django.shortcuts import render
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Event


# db conn
def run_query(request):
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=MAORYZEN7\SQLEXPRESS;'
                          'Database=CS6400;'
                          'Trusted_Connection=yes;')
    cursor = conn.cursor()
    # result = []
    cursor.execute("SELECT v.VIN,VehicleType.Vehicle_type,v.Year,v.Manufacturer_name,v.Model_name,V.Description, color = ( SELECT DISTINCT STRING_AGG(c.Color,' | ') FROM Color c WHERE c.VIN=v.VIN),v.List_price FROM Vehicle v LEFT JOIN (SELECT Car.VIN, 'Car' AS Vehicle_type FROM Car UNION	SELECT SUV.VIN, 'SUV' AS Vehicle_type FROM SUV UNION	SELECT Truck.VIN, 'Truck' AS Vehicle_type FROM Truck UNION	SELECT Convertible.VIN, 'Convertible' AS Vehicle_type FROM Convertible UNION	SELECT VanMinivan.VIN, 'VanMinivan' AS Vehicle_type FROM VanMinivan ) AS VehicleType ON v.VIN= vehicleType.VIN")
    #result = cursor.fetchall()

    # get header and rows
    header = [i[0] for i in cursor.description]
    result = [list(i) for i in cursor.fetchall()]
    # append header to rows
    result.insert(0, header)
    cursor.close()

    #cnx.close()
    #return rows

    return render(request, 'events/showsql.html', {'result': result, 'header': header})


# Create your views / functions here
def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    first_name = "Mao"
    month = month.title()
    # convert from name to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)
    # create calendar
    cal = HTMLCalendar().formatmonth(year, month_number)
    # get current date
    now = datetime.now()
    current_year = now.year
    # get current time
    time = now.strftime('%I:%M: %p')

    return render(request,
                  'events/home.html', {
                      "first_name": first_name
                      , "year": year
                      , "month": month
                      , "month_number": month_number
                      , "cal": cal, "current_year": current_year
                      , "time": time
                  })


def all_events(request):
    event_list = Event.objects.all()
    return render(request, 'events/event_list.html', {
        'event_list': event_list})
