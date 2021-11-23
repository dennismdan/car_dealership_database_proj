import os

from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import LoginForm, QueryVehicleForm, ReportTypes, LookupCustomer, FilterBy, AddCustomer, Individual, Business
from .forms import AddRepair
from .utils import run_query, get_search_vehicle_query
from .runtime_constants import USER_ROLE

USER_ROLE = os.environ["USER_ROLE"]
'''
TODO: 
list all business constraint 
make sure that we implement ALL constraints in our code 
https://jacobian.org/2010/feb/28/dynamic-form-generation/
'''


def home(request):
    view_inventory = False
    data = []
    header = []
    form = QueryVehicleForm()
    if request.method == 'POST':
        form = QueryVehicleForm(request.POST)
        if form.is_valid():
            print("POST statement from home page")
            user_input = form.extract_data()

            query = get_search_vehicle_query(user_input)
            print(query)

            data, header = run_query(query)
    else:
        form = QueryVehicleForm()

    vehicle_count = run_query("SELECT COUNT(*) FROM Vehicle")[0][0][0]

    return render(request, 'mainlanding/home.html',
                  {'form': form,
                   'data': data,
                   'user':os.environ["USER_ROLE"],
                   'vehicle_count':vehicle_count,
                   'header': header})


def base(request):
    print("base")
    return render(request, 'mainlanding/base.html')


# def add_vehicle(request):
#     print("vehicle")
#     VIN = "VIN"
#     # if this is a POST request we need to process the form data
#     if request.method == 'POST':
#         # create a form instance and populate it with data from the request:
#         form = AddVehicle(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
#             # process the data in form.cleaned_data as required
#             VIN = AddVehicle().cleaned_data['VIN']
#             # ...
#             # redirect to a new URL:
#             # return HttpResponseRedirect('/thanks/')
#     # if a GET (or any other method) we'll create a blank form
#     else:
#         form = AddVehicle()
#     # print("add_vehicle")
#     return render(request, 'mainlanding/add_vehicle.html', {'form': form})


def reports(request):
    print("reports")
    form = ReportTypes()
    return render(request, 'mainlanding/reports.html', {'form': form})


def repairs(request):
    print("repairs")
    return render(request, 'mainlanding/repairs.html')


def click(request):
    print("clicked")
    return render(request, 'mainlanding/clicked.html')


def login(request):
    return render(request, 'mainlanding/loging.html')


def filter_vehicles(request):
    print("filter")
    form = FilterBy()
    return render(request, 'mainlanding/filter.html', {'form': form})


def lookup_customer(request):
    view_inventory = False
    data = []
    header = []

    form = LookupCustomer()

    return render(request, 'mainlanding/lookup_customer.html',
                  {'form': form,
                   'data': data,
                   'header': header})

def add_customer(request):
    view_inventory = False
    data = []
    header = []

    form = AddCustomer()

    return render(request, 'mainlanding/add_customer.html',
                  {'form': form,
                   'data': data,
                   'header': header})

def individual(request):
    view_inventory = False
    data = []
    header = []

    form = Individual()

    return render(request, 'mainlanding/individual.html',
                  {'form': form,
                   'data': data,
                   'header': header})

def business(request):
    view_inventory = False
    data = []
    header = []

    form = Business()

    return render(request, 'mainlanding/business.html',
                  {'form': form,
                   'data': data,
                   'header': header})


def loggedin(request):
    data = None
    header = None
    if request.method == "POST":
        # Get the posted form
        form = LoginForm(request.POST)
        user_input = form.data.dict()
        print("User Logging in as: ",user_input["users"])
        os.environ["USER_ROLE"] = user_input["users"]

        form = QueryVehicleForm()
    else:
        form = LoginForm()

    vehicle_count = run_query("SELECT COUNT(*) FROM Vehicle")[0][0][0]

    return render(request, 'mainlanding/home.html',
                  {'form': form,
                   'data': data,
                   'user':os.environ["USER_ROLE"],
                   'vehicle_count':vehicle_count,
                   'header': header})

def add_repair(request):
    view_inventory = False
    data = []
    header = []

    form = AddRepair()

    return render(request, 'mainlanding/add_repair.html',
                  {'form': form,
                   'data': data,
                   'header': header})


def total_vehicles_available():
    pass

def add_vehicle():
    pass

