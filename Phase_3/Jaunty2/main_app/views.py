import os
from datetime import datetime
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
                    SelectVehicleTypeForm,
                    FindRepairForm,
                    AddPartForm,
                    AddRepairForm,
                    RepairForm)
from .forms import AddRepair
from .utils import run_query, get_search_vehicle_query, run_reports,insert_row,get_data_for_template_report
from .utils import (run_query,
                    gen_query_add_row,
                    get_search_vehicle_query,
                    get_detailed_vehicle_query,
                    cleanup_null_cols,
                    get_sales_query,
                    insert_row,
                    get_repair_query,
                    get_data_for_template,
                    find_customer,
                    get_query_with_condition,
                    stage_repair_data,
                    update_row,
                    gen_query_update_row,
                    get_query_from_file,
                    update_table
                    )
from .runtime_constants import USER_ROLE
from .utils import get_data_for_template_customerdrill,get_data_for_template_repairby_manutypemodel

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

    vehicle_count = run_query("SELECT COUNT(*) FROM Vehicle v WHERE v.VIN NOT IN( SELECT s.VIN FROM Sale s)")[0][0][0]

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
    report_type = ""

    if request.method == 'POST':
        form = ReportTypes(request.POST)

        if form.is_valid():

            user_input = form.extract_data()
            query = run_reports(user_input)  # generate query
            report_type = user_input["reports"]

            data, header = run_query(query)  # run query
            if len(data) == 0:
                home_status = "No data available"
            else:
                home_status = "Results found and displayed below."
        else:
            home_status = "Inputs fields need to be corrected."
    else:
        form = ReportTypes()

    context = {'form': form,
                   'data': data,
                   'report_type':report_type,
                   'status': home_status,
                   'user': os.environ["USER_ROLE"],
                   'header': header}


    return render(request, 'mainlanding/reports.html',
                  context)


def monthlysales_drilldown(request,year,month):

    drill_data = {'header':[], 'data':[()]}

    if os.environ["USER_ROLE"] in ["manager", "owner"]:
        drill_data = get_data_for_template_report(year, month)

    context = {"user": os.environ["USER_ROLE"],
               "year": year,
               "month": month,
               'drill_data': drill_data,
               "full_users":["manager", "owner"],

               }

    return render(request,
                  'mainlanding/monthly_sales_details.html',
                  context)

def gross_customer_income_drilldown(request,Customer_id):
    sales_data = {'header': [], 'data': [()], "status": ""}
    repair_data = {'header': [], 'data': [()], "status": ""}

    if os.environ["USER_ROLE"] in ["manager", "owner"]:
        sales_data = get_data_for_template_customerdrill(Customer_id, query_type="sales")
        repair_data = get_data_for_template_customerdrill(Customer_id, query_type="repair")

    context = {"user": os.environ["USER_ROLE"],
               "Customer_id": Customer_id,
               "full_users": ["manager", "owner"],
               'sales_data': sales_data,
               'repair_data': repair_data}

    return render(request,
                  'mainlanding/gross_customer_details.html',
                  context)


def repairsby_manu_type_model_drill(request,manufacturer_name):
    one_data = {'header':[], 'data':[()], "status":""}
    two_data = {'header':[], 'data':[()], "status":""}


    if os.environ["USER_ROLE"] in ["manager","owner"]:
        one_data = get_data_for_template_repairby_manutypemodel(manufacturer_name,query_type="one")
        two_data = get_data_for_template_repairby_manutypemodel(manufacturer_name,query_type="two")

    context = {"user": os.environ["USER_ROLE"],
               "manufacturer_name": manufacturer_name,
               "full_users":["manager","owner"],
               'one_data': one_data,
               'two_data': two_data}


    return render(request,
                  'mainlanding/repairby_manutypemodel_details.html',
                  context)

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
    path = request.path

    customer_type = path[1:-1]

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

    vehicle_count = run_query("SELECT COUNT(*) FROM Vehicle v WHERE v.VIN NOT IN( SELECT s.VIN FROM Sale s)")[0][0][0]

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
    status = ""
    message_class = "normal"
    customer_type = ""
    customer_status = {"status": status, "css_class": message_class}
    customer_type_status = {"status": status, "css_class": message_class}


    # message_class = "normal"

    if request.method == 'POST':
        form = AddCustomer(request.POST)

        if form.is_valid():
            row,row_type,customer_type = form.extract_data()

            if len(row)!=0:
                query = gen_query_add_row(table_name="Customer", row=row, skip_col_list=["Customer_id"])
                status,css_class = insert_row(query, row)
                customer_status = {"status": status, "css_class": css_class}

                colnames = ["Phone_number","Email","Street_address","City","State","Postal_code"]
                where_clause = " AND ".join([f"{colnames[i]} = '{row[i]}'" for i in range(len(row))])
                query = "SELECT Customer_id FROM Customer WHERE "+where_clause
                customer_id = run_query(query)[0][0][0]
            if len(row_type)==3:
                row_type.insert(1,customer_id)
                query = gen_query_add_row(table_name="Person", row=row_type)
                status,css_class= insert_row(query, row_type)

            else:
                row_type.insert(1,customer_id)
                query = gen_query_add_row(table_name="Business", row=row_type)
                status,css_class = insert_row(query, row_type)

            customer_type_status = {"status": status, "css_class": css_class}

    return render(request, 'mainlanding/add_customer.html',
                  {'form': form,
                   'customer_type':customer_type,
                   'customer_status':customer_status,
                   'customer_type_status':customer_type_status,
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
    form = FindRepairForm()
    view_type = "find_repair"
    status = ""
    css_class = "normal"
    status = {"status":status,"css_class":css_class}

    if request.method == 'POST':
        form = FindRepairForm(data=request.POST)
        if form.is_valid():
            row_dict, edit_allowed = form.extract_data()
            data, edit_cols, status,css_class = stage_repair_data(row_dict, edit_allowed)
            status = {"status": status, "css_class": css_class}
            add_repair = False
            form = RepairForm(init_data = data,
                              edit_fields = edit_cols,
                              add_repair = add_repair)

            if edit_allowed and edit_cols:
                view_type = "edit_repair"

            else:
                view_type = "view_repair"

    return render(request,
                  'mainlanding/repairs.html',
                  {'user':os.environ["USER_ROLE"],
                   "form":form,
                   "status":status,
                   "view_type":view_type,
                   })

def add_repair(request):
    cols = ["VIN", "Customer_id", "Start_date", "Labor_charges",
            "Total_cost", "Description", "Completion_date", "Odometer_reading", "Username"]
    init_data = {cols[i]: "" for i in range(len(cols))}

    add_repair_form = RepairForm(init_data = init_data,
                                 edit_fields=[],
                                 add_repair=True)
    view_type = "add_repair"
    status = ""
    css_class = "normal"
    status = {"status":status,"css_class":css_class}

    if request.method == 'POST':
        add_repair_form = RepairForm(data=request.POST,
                                     init_data = init_data,
                                     edit_fields=[],
                                     add_repair=True
                                     )
        if add_repair_form.is_valid():
            row = add_repair_form.extract_data()
            query = gen_query_add_row("Repair",row)
            status,css_class = insert_row(query,row)
            status = {"status": status, "css_class": css_class}

            if status["css_class"] == "success":
                primary_keys = {"VIN": row[0],
                             "Customer_id": row[1],
                             "Start_date": row[2]}
                total_cost_update_status = update_total_cost(primary_keys)

                print("Total Cost Update Status: ", total_cost_update_status)

    return render(request,
                  'mainlanding/repairs.html',
                  {'user':os.environ["USER_ROLE"],
                   "form":add_repair_form,
                   "status":status,
                   "view_type":view_type,
                   })

def view_part(request,VIN,Customer_id,Start_date):
    view_type = "view_part"
    header = []
    data = []
    Start_date = datetime.strptime(Start_date,'%Y-%m-%d %H:%M:%S')

    init_data={"VIN":VIN,
               "Customer_id":Customer_id,
               "Start_date":Start_date}

    query = f"SELECT * FROM Part WHERE VIN = '{VIN}' AND Customer_id = '{Customer_id}' AND Start_date = '{Start_date}'"
    data, header = run_query(query)
    status = "Found parts to review for this repair."
    css_class = "success"
    if not data:
        header = []
        status = "No parts found for this repair."
        css_class = "warning"
    status = {"status": status, "css_class": css_class}
    return render(request,
                  'mainlanding/repairs.html',
                  {'user': os.environ["USER_ROLE"],
                   "header": header,
                   "data": data,
                   "view_type": view_type,
                   "status":status,
                   "init_data": init_data
                   })

def add_part(request,VIN,Customer_id,Start_date):
    view_type = "add_part"
    add_part_status = {"status": "", "css_class": ""}
    existing_part_status = {"status": "", "css_class": ""}

    header = []
    data = []
    Start_date = datetime.strptime(Start_date,'%Y-%m-%d %H:%M:%S')

    init_data={"VIN":VIN,
               "Customer_id":Customer_id,
               "Start_date":Start_date}
    lookup_part_data = init_data.copy()

    form = AddPartForm(init_data=init_data)

    data,header,existing_part_status  = part_lookup(lookup_part_data)

    if request.method == 'POST':
        form = AddPartForm(data=request.POST,init_data=init_data)
        if form.is_valid():
            row = form.extract_data()
            query = gen_query_add_row("Part",row)
            status,css_class = insert_row(query,row)
            add_part_status = {"status": status, "css_class": css_class}

            form = AddPartForm(init_data=init_data)

            data, header, existing_part_status = part_lookup(lookup_part_data)

    return render(request,
                  'mainlanding/repairs.html',
                  {'user':os.environ["USER_ROLE"],
                   "form":form,
                   "header":header,
                   "data":data,
                   "add_part_status":add_part_status,
                   "existing_part_status":existing_part_status,
                   "view_type":view_type,
                   "init_data":init_data
                   })

def part_lookup(init_data):
    where_clause = " AND ".join([f"{k} = '{v}'" for k, v in init_data.items()])
    query = "SELECT * FROM Part WHERE " + where_clause

    data, header = run_query(query)
    status = "Found parts to review for this repair."
    css_class = "success"
    if not data:
        header = []
        status = "No parts found. Add parts for this repair."
        css_class = "warning"
    status = {"status": status, "css_class": css_class}

    return data, header, status

def edit_repair(request,VIN,Customer_id,Start_date):
    row_dict = {"VIN":VIN,
               "Customer_id":Customer_id,
               "Start_date":Start_date}
    primary_keys = row_dict.copy()

    edit_allowed = True
    data, edit_cols, status, css_class = stage_repair_data(row_dict, edit_allowed)
    status = {"status": status, "css_class": css_class}
    add_repair = False
    view_type = "edit_repair"

    form = RepairForm(init_data=data,
                      edit_fields=edit_cols,
                      add_repair=add_repair)

    if request.method == 'POST':

        form = RepairForm(data=request.POST,
                          init_data=data,
                          edit_fields=edit_cols,
                          add_repair=add_repair)
        if form.is_valid():
            repairs = form.extract_data()
            if repairs is not None:
                update_fields = repairs["update_fields"]
                where_fields = repairs["where_fields"]

                query = gen_query_update_row("Repair", update_fields, where_fields)
                status, css_class = update_row(query)
                status = {"status": status, "css_class": css_class}
                total_cost_update_status, total_cost_status = update_total_cost(primary_keys)
                print("Total Cost Update Status: ", total_cost_update_status)
    return render(request,
                  'mainlanding/repairs.html',
                  {'user':os.environ["USER_ROLE"],
                   "form":form,
                   "status":status,
                   "view_type":view_type,
                   })

def close_repair(request,VIN,Customer_id,Start_date):
    row_dict = {"VIN":VIN,
               "Customer_id":Customer_id,
               "Start_date":Start_date}
    edit_allowed = True
    data, edit_cols, status, css_class = stage_repair_data(row_dict, edit_allowed)
    status = {"status": status, "css_class": css_class}

    view_type = "edit_repair"

    form = RepairForm(init_data=data,
                      edit_fields=edit_cols,
                      add_repair=False)

    total_cost_update_status, total_cost_status = update_total_cost(row_dict)

    print("Total Cost Update Status: ", total_cost_update_status)

    status,css_class = check_closing_data(data)

    if css_class == "success" and total_cost_status == "success":
        view_type = "view_repair"
        form = RepairForm(init_data=data,
                          edit_fields=[],
                          add_repair=False)
    css_class = "success" if all([css_class,total_cost_status]) else "error"
    status = {"status": status+total_cost_update_status, "css_class": css_class}
    return render(request,
                  'mainlanding/repairs.html',
                  {'user':os.environ["USER_ROLE"],
                   "form":form,
                   "status":status,
                   "view_type":view_type,
                   })

def check_closing_data(data):
    fail_values = [None,""]
    check_fields = ["Labor_charges", "Total_cost","Completion_date"]
    status = ""
    for field in check_fields:
        if data[field] in fail_values:
            status+= f"Field {field} cannot be empty. "

    if status == "":
        status = "Repair successfully closed."
        css_class = "success"
    else:
        css_class = "error"

    return status,css_class

def update_total_cost(primary_keys):
    query = get_query_from_file("update_total_cost.txt")
    VIN = primary_keys["VIN"]
    Customer_id = primary_keys["Customer_id"]
    Start_date = primary_keys["Start_date"]
    query+= f" r.VIN = '{VIN}' and r.Customer_id = '{Customer_id}' and r.Start_date = '{Start_date}'"
    status, css_status = update_table(query)
    return status+" "+css_status, css_status

