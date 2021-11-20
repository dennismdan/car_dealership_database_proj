from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import LoginForm, QueryVehicleForm, ReportTypes, LookupCustomer, FilterBy, AddCustomer
from .utils import run_query, generate_query

'''
TODO: 
list all business constraint 
make sure that we implement ALL constraints in our code 
'''


def home(request):
    view_inventory = False
    data = []
    header = []

    if request.method == 'POST':
        form = QueryVehicleForm(request.POST)
        print("POST statement from home page")
        user_input = form.data.dict()
        query = generate_query(user_input)
        data, header = run_query(query)
    else:
        form = QueryVehicleForm()
    #
    #     if form.is_valid():
    #         # TODO: run the search vihicle query function
    #         '''
    #         query = generate_query(form.data)
    #         data = run_query(query)
    #         '''
    #         #return HttpResponseRedirect('/home?view_inventory=True')
    #     else:
    #         '''
    #         TODO: handle form when format doesn't match expectation
    #         Copy error handling from bootstrap templates
    #         '''
    #         data = form.data.dict()
    #     form = QueryVehicleForm()
    # else:
    #     print("welcome home")
    #     form = QueryVehicleForm()

    print("data: ", data)
    print("header: ", header)

    return render(request, 'mainlanding/home.html',
                  {'form': form,
                   'data': data,
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


def loggedin(request):
    username = "username"

    print()

    if request.method == "POST":
        # Get the posted form
        MyLoginForm = LoginForm(request.POST)

        if MyLoginForm.is_valid():
            username = MyLoginForm.cleaned_data['username']
    else:
        MyLoginForm = LoginForm()

    return render(request, 'mainlanding/home.html')


def total_vehicles_available():
    pass

def add_vehicle():
    pass

