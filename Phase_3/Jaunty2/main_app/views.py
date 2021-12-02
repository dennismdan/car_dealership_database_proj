import os

from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import (LoginForm,
                    QueryVehicleForm,
                    ReportTypes,
                    LookupCustomer,
                    FilterBy,
                    AddCustomer,
                    SellVehicle,
                    AddVehicleForm,
                    SelectVehicleTypeForm)
from .forms import AddRepair
from .utils import run_query, get_search_vehicle_query, run_reports,insert_row
from .utils import (run_query,
                    gen_query_add_row,
                    get_search_vehicle_query,
                    get_detailed_vehicle_query,
                    cleanup_null_cols,
                    get_sales_query,
                    insert_row,
                    get_repair_query,
                    get_data_for_template,
                    find_customer)
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

def update_add_customer(request, ):
    home_status = "Setting the add customer template with individual or business."
    print(home_status)
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

def total_vehicles_available():
    pass

def vehicle_details(request,vin):
    '''
    https://stackoverflow.com/questions/29153593/passing-variable-from-django-template-to-view
    :param request:
    :return:
    '''

    sales_data = {'header':[], 'data':[()], "status":""}
    repair_data = {'header':[], 'data':[()], "status":""}

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
    # data = []
    # header = []
    form = AddCustomer()
    # home_status = "Add New Customer."
    status = " "
    # message_class = "normal"

    if request.method == 'POST':
        form = AddCustomer(request.POST)

        if form.is_valid():
            row,row_type = form.extract_data()
            print(row)
            print(row_type)



            try:
                if len(row)!=0:
                    query = gen_query_add_row(table_name="Customer", row=row)
                    insert_row(query, row)

                if len(row_type)==3:
                    query = gen_query_add_row(table_name="Person", row=row_type)
                    insert_row(query, row_type)
                else:

                    query = gen_query_add_row(table_name="Business", row=row_type)
                    insert_row(query, row_type)
                status = 'Customer added successfully!'





            except:
                status = 'There was an error adding new customer. Please try again!.'


    return render(request, 'mainlanding/add_customer.html',
                  {'form': form,

                   'status':status,
                   'user':os.environ["USER_ROLE"],
                   })

def lookup_customer(request):
    data = []
    header = []
    form = LookupCustomer()
    status = "Look up either business or person customer."

    if request.method == 'POST':
        form = LookupCustomer(request.POST)

        if form.is_valid():
            user_data = form.extract_data()
            Driver_license = user_data['drivers_licens_nr']
            Tin = user_data['tin']

            data,header,status = find_customer(Driver_license,Tin)

    else:
        form = LookupCustomer()



    return render(request, 'mainlanding/lookup_customer.html',
                  {'form': form,
                   'status':status,
                   'data':data,
                   'header':header,
                   'user':os.environ["USER_ROLE"],
                   'header': header})

def sell_vehicle(request,vin):
    query = f"SELECT Invoice_price FROM Vehicle WHERE VIN = '{vin}'"

    data, _ = run_query(query)
    invoice_price = data[0][0]

    form = SellVehicle(vin,invoice_price)
    status = ""
    message_class = "normal"


    if request.method == 'POST':
        form = SellVehicle(data=request.POST, vin=vin,invoice_price=invoice_price)

        if form.is_valid():
            row = form.extract_data()
            try:
                query = gen_query_add_row(table_name="Sale",row = row)
                insert_row(query, row)
                status = 'Congratulations, the vehicle sold successfully!'
                message_class = "success"
            except:
                status = 'There was an issue selling the vehicle. Please contact IT.'
                message_class = "error"

    return render(request, 'mainlanding/sell_vehicle.html',
                  {
                      "form": form,
                      "vin": vin,
                      "status": status,
                      "message_class":message_class,
                      'user': os.environ["USER_ROLE"]
                  }
                  )

def add_vehicle(request):
    add_vehicle_form = AddVehicleForm()
    vehicle_type_form = SelectVehicleTypeForm()
    status = ""
    message_class = "normal"
    color = {"status": status, "css_class": message_class}
    vehicle_type = {"status": status, "css_class": message_class}
    vehicle = {"status": status, "css_class": message_class}
    manu = {"status": status, "css_class": message_class}

    if request.method == 'POST':
        add_vehicle_form = AddVehicleForm(data=request.POST)

        if add_vehicle_form.is_valid():

            manufacturer_row,vehicle_row,car_type_dict,color_data = add_vehicle_form.extract_data()

            print("Adding Manufacturer")
            query = gen_query_add_row(table_name="Manufacturer", row=manufacturer_row)
            status_manu,class_manu = insert_row(query, manufacturer_row)
            manu = {"status":status_manu,"css_class":class_manu}

            print("Adding Vehicle")
            query = gen_query_add_row(table_name="Vehicle",row = vehicle_row,skip_col_list=["List_price"])
            status_vehicle,class_vehicle = insert_row(query, vehicle_row)
            vehicle = {"status": status_vehicle, "css_class": class_vehicle}

            print("Adding Vehicle Type Data")
            table = car_type_dict["type"]
            row = car_type_dict["data"]
            query = gen_query_add_row(table_name=table,row = row)
            status_vehicle_type,class_vehicle_type = insert_row(query, row)
            vehicle_type = {"status": status_vehicle_type, "css_class": class_vehicle_type}

            print("Adding Colors")
            for row in color_data:
                query = gen_query_add_row(table_name="Color", row=row)
                status_color,class_color = insert_row(query, row)
                color = {"status": status_color, "css_class": class_color}


    return render(request, 'mainlanding/add_vehicle.html',
                  {   "color":color,
                      "vehicle_type":vehicle_type,
                      "vehicle":vehicle,
                      "manu":manu,
                      "vehicle_type_form": vehicle_type_form,
                      "add_vehicle_form": add_vehicle_form,
                      "status": status,
                      "message_class":message_class,
                      'user': os.environ["USER_ROLE"]
                  }
                  )

def update_vehicle_type(request):

    add_vehicle_form = AddVehicleForm()
    vehicle_type_form = SelectVehicleTypeForm()

    status = ""
    message_class = "normal"
    color = {"status": status, "css_class": message_class}
    vehicle_type = {"status": status, "css_class": message_class}
    vehicle = {"status": status, "css_class": message_class}
    manu = {"status": status, "css_class": message_class}

    if request.method == 'POST':
        vehicle_type_form = SelectVehicleTypeForm(data=request.POST)

        if vehicle_type_form.is_valid():
            vehicle_type = vehicle_type_form.extract_data()
            print("Updated Add Vehicle Form to vehicle type ", vehicle_type)
            os.environ["VEHICLE_TYPE"] = vehicle_type

            add_vehicle_form = AddVehicleForm()

    return render(request, 'mainlanding/add_vehicle.html',
                  {   "color":color,
                      "vehicle_type":vehicle_type,
                      "vehicle":vehicle,
                      "manu":manu,
                      "vehicle_type_form": vehicle_type_form,
                      "add_vehicle_form": add_vehicle_form,
                      "status": status,
                      "message_class":message_class,
                      'user': os.environ["USER_ROLE"]
                  }
                  )


def repairs(request):
    print("repairs")
    return render(request,
                  'mainlanding/repairs.html',
                  {'user':os.environ["USER_ROLE"]})

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

def update_repair(request):
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

def add_part(request):
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