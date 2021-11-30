import os

from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import (LoginForm,
                    QueryVehicleForm,
                    ReportTypes,
                    LookupCustomer,
                    FilterBy,
                    AddCustomer,
                    SellVehicle)
from .forms import AddRepair
from .utils import run_query, get_search_vehicle_query, run_reports,insert_row
from .utils import (run_query,
                    get_search_vehicle_query,
                    get_detailed_vehicle_query,
                    cleanup_null_cols,
                    get_sales_query,
                    get_repair_query,
                    get_data_for_template)
from .runtime_constants import USER_ROLE

USER_ROLE = os.environ["USER_ROLE"]
#home_form_state = None #instantiate global variable


'''
TODO: 
list all business constraint 
make sure that we implement ALL constraints in our code 
https://jacobian.org/2010/feb/28/dynamic-form-generation/
https://javascript.tutorialink.com/using-javascript-onclick-event-to-pass-data-to-views-py-in-django/
'''


def home(request):
    data = []
    header = []
    form = QueryVehicleForm()
    home_status = "Search available inventory."

    if request.method == 'POST':
        form = QueryVehicleForm(request.POST)

        if form.is_valid():
            print("POST statement from home page")
            user_input = form.extract_data()
            query = get_search_vehicle_query(user_input) # generate query
            data, header = run_query(query) # run query

            if len(data) == 0:
                home_status = "Sorry, it looks like we don’t have that in stock!"
            else:
                home_status = "Results found and displayed below."
        else:
            home_status = "Inputs fields need to be corrected."

    else:
        form = QueryVehicleForm()

    vehicle_count = run_query("SELECT COUNT(*) FROM Vehicle")[0][0][0]

    return render(request, 'mainlanding/home.html',
                  {'form': form,
                   'data': data,
                   'status':home_status,
                   'user':os.environ["USER_ROLE"],
                   'vehicle_count':vehicle_count,
                   'header': header})


def base(request):
    print("base")
    return render(request, 'mainlanding/base.html',{
                   'user':os.environ["USER_ROLE"]})


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
    data = []
    header = []
    form = ReportTypes()
    home_status = "Get Reports."
    if request.method == 'POST':
        form = ReportTypes(request.POST)

        if form.is_valid():

            user_input = form.extract_data()
            query = run_reports(user_input)  # generate query

            data, header = run_query(query)  # run query
            if len(data) == 0:
                home_status = "No data available"
            else:
                home_status = "Results found and displayed below."
        else:
            home_status = "Inputs fields need to be corrected."
    else:
        form = ReportTypes()

    return render(request, 'mainlanding/reports.html',
                  {'form': form,
                   'data': data,
                   'status': home_status,
                   'user': os.environ["USER_ROLE"],
                   'header': header})



def repairs(request):
    print("repairs")
    return render(request, 'mainlanding/repairs.html',
                  {
                   'user':os.environ["USER_ROLE"]})


def click(request):
    print("clicked")
    return render(request, 'mainlanding/clicked.html',
                  {'user':os.environ["USER_ROLE"]})


def login(request):
    users = {"regular_user": "Regular User",
             "manager": "Manager",
             "inventory_clerk": "Inventory Clerk",
             "service_writer": "Service Writer",
             "sales_person": "Sales Person",
             "owner": "Owner"}
    current_role = os.environ["USER_ROLE"]

    return render(request, 'mainlanding/loging.html',
                  {"users":users,
                   "current_role":current_role,
                  'user':os.environ["USER_ROLE"]
                   })

def filter_vehicles(request):
    print("filter")
    form = FilterBy()
    return render(request, 'mainlanding/filter.html',
                  {'form': form,
                   'user':os.environ["USER_ROLE"]})


# def lookup_customer(request):
#     view_inventory = False
#     data = []
#     header = []
#
#     form = LookupCustomer()
#
#     return render(request, 'mainlanding/lookup_customer.html',
#                   {'form': form,
#                    'data': data,
#                    'header': header})

# def add_customer(request):
#     view_inventory = False
#     data = []
#     header = []
#
#     form = AddCustomer()
#
#     return render(request, 'mainlanding/add_customer.html',
#                   {'form': form,
#                    'data': data,
#                    'header': header})

def update_add_customer(request, ):
    home_status = "Setting the add customer template with individual or business."

    path = request.path

    customer_type = path[1:-1]
    print("Customer set to: ",customer_type)

    os.environ["ADD_USER_TYPE"] = customer_type
    form = AddCustomer()

    return render(request, 'mainlanding/add_customer.html',
                  {'form': form,
                  'user':os.environ["USER_ROLE"],
                   'customer':customer_type})


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
                   'status': "Search available inventory.",
                   'data': data,
                   'user':os.environ["USER_ROLE"],
                   'vehicle_count':vehicle_count,
                   'header': header})

def add_repair(request):
    data = None
    header = None
    if request.method == 'POST':
        form = AddRepair(request.POST)

        if form.is_valid():

            user_input = form.extract_data()
            print(user_input)
            query = add_repair(user_input)  # generate query
            data = insert_row(query)
            # data = insert_row(query, "user_input")
            #data, header = run_query(query)  # run query
            if len(data) == 0:
                home_status = "No data available"
            else:
                home_status = "Results found and displayed below."
        else:
            home_status = "Inputs fields need to be corrected."

    else:
        form = AddRepair()

    return render(request, 'mainlanding/add_repair.html',
                  {'form': form,
                   'data': data,
                  'user':os.environ["USER_ROLE"],
                   'header': header})


def total_vehicles_available():
    pass

def add_vehicle():
    pass

def vehicle_details(request,vin):
    '''
    https://stackoverflow.com/questions/29153593/passing-variable-from-django-template-to-view
    :param request:
    :return:
    '''

    sales_data = {'header':[], 'data':[], "status":""}
    repair_data = {'header':[], 'data':[], "status":""}

    vehicle_data = get_data_for_template(vin,query_type="vehicle")

    if os.environ["USER_ROLE"] in ["manager","owner"]:
        sales_data = get_data_for_template(vin,query_type="sales")
        repair_data = get_data_for_template(vin,query_type="repair")

    context = {"user": os.environ["USER_ROLE"],
               "vin":vin,
               "full_users":["manager","owner"],
               'vehicle_data': vehicle_data,
               'sales_data': sales_data,
               'repair_data': repair_data}

    return render(request,
                  'mainlanding/vehicle_details.html',
                  context)

def add_customer(request):
    data = []
    header = []
    form = AddCustomer()
    home_status = "Add New Customer."

    if request.method == 'POST':
        form = AddCustomer(request.POST)

        if form.is_valid():
            print("Add New Customer")
            user_input = form.extract_data()
            query = add_customer_query(user_input) # generate query, get_search_vehicle_query(user_input)
            data, header = run_query(query) # run query

            if len(data) == 0:
                home_status = "Please fill the required field"
            else:
                home_status = "Added successfully "
        else:
            home_status = "Inputs fields need to be corrected."

    else:
        form = AddCustomer()

    return render(request, 'mainlanding/add_customer.html',
                  {'form': form,
                   'data': data,
                   'status':home_status,
                   'user':os.environ["USER_ROLE"],
                   'header': header})

def lookup_customer(request):
    data = []
    header = []
    form = LookupCustomer()
    home_status = "Search Customer."

    if request.method == 'POST':
        form = LookupCustomer(request.POST)

        if form.is_valid():

            user_input = form.extract_data()
            query = lookup_customer_query(user_input) # generate query
            data, header = run_query(query) # run query

            if len(data) == 0:
                home_status = "Sorry, it looks like we don’t have that customer!"
            else:
                home_status = "Results found and displayed below."
        else:
            home_status = "Inputs fields need to be corrected."

    else:
        form = LookupCustomer()



    return render(request, 'mainlanding/lookup_customer.html',
                  {'form': form,
                   'data': data,
                   'status':home_status,
                   'user':os.environ["USER_ROLE"],
                   'header': header})

def sell_vehicle(request,vin):
    form = SellVehicle()
    context = {
        "form":form,
        "vin":vin,
        'user': os.environ["USER_ROLE"]
               }
    print("Selling vehicle with vin: ", vin)
    return render(request, 'mainlanding/sell_vehicle.html',context)
