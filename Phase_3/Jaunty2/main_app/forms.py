import os

from django import forms
import main_app.views

from django.core.exceptions import ValidationError
from main_app.utils import (get_colors,
                            get_manufacturer_names,
                            run_reports,
                            find_customer,
                            get_customer_id,
                            run_query,check_if_instance_exists)

from datetime import datetime, date, timedelta
from pytz import timezone
import os

timezone_est = timezone('EST')

workers = ["owner","manager","inventory_clerk","sales_person","service_writer"] # only role "regular_user" missing

'''
Pass forms to html
https://djangobook.com/mdj2-django-forms/

Dynamic Forms: 
https://www.b-list.org/weblog/2008/nov/09/dynamic-forms/

TODO: apply business constraints   
'''

def validate_decimals(value):
    values=str(value).split(".")
    two_parts = len(values)
    if two_parts==2:
        if len(values[1])==2:
            return round(float(value), 2)
        else:
            raise ValidationError(
                ('%(value)s is not with two decimal places (ex: 10.00)'),
                params={'value': value})

    else:
        raise ValidationError(
            ('%(value)s is not a float'),
            params={'value': value})

def price_check(sales_price):
    invoice_price = round(float(os.environ["SALES_INVOICE_PRICE"]),2)

    if os.environ["USER_ROLE"]=="owner":
        return sales_price

    elif sales_price <= invoice_price*0.95:
        raise ValidationError(
            (f'Sales price of {sales_price} is <= than {invoice_price*0.95} (invoice_price*0.95). Only the owner can perform this sell'))
    else:
        return sales_price

def business_lookup(id):
    if id == "":
        return id
    else:
        data,_,_ = find_customer("",id)
        if len(data)==0:
            raise ValidationError(
                ('Customer not found in business customers, please add customer'))
        else:
            return id

def person_lookup(id):
    if id == "":
        return id
    else:
        data,_,_ = find_customer(id,"")

        if len(data)==0:
            raise ValidationError(
                ('Customer not found in persons customers, please add customer'))
        else:
            return id

def date_check(date):
    today = datetime.now(timezone_est)
    tomorrow = today + timedelta(days=1)
    far_past = today - timedelta(days=7)

    if  date >= tomorrow:
        raise ValidationError(
            ('Sale date cannot be in the future, unless you are a time traveler :P'))
    elif date <= far_past:
        raise ValidationError(
            ('Sale date cannot be more than a week into the past, unless you want to travel back to the future after you sell it in the past :P'))
    else:
        return date

def employee_lookup(username):
    query = f"SELECT Username FROM EmployeeUser Where Username = '{username}'"
    data, _  = run_query(query)

    if len(data)==0:
        raise ValidationError((
            f"Employee with username {username} not currently on staff"
        ))
    else:
        return username

def check_vin_esitance(vin):

    value_exists = check_if_instance_exists("Vehicle",["VIN"],[("VIN",vin)])

    if value_exists:
        raise ValidationError((
            f"Vehicle VIN already in inventory"
        ))
    else:
        return vin

class LoginForm(forms.Form):
    user = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())

class QueryVehicleForm(forms.Form):
    '''
   TODO: right now color chices are hard coded
   we want to retrieve these with a query pass as parameter
   TODO: Vehicle type, manufacturer name, and model year, keyword is a drop down
   '''
    color_choices = get_colors()
    vehicle_choices = [(0,"Car"),(1,"Convertible"),(2,"SUV"),(3,"Truck"),(4,"VanMinivan"),(5,"all")]
    sold_unsold_options = [(0, "all"), (1, "sold"), (2, "unsold")]
    manufacturer_names = get_manufacturer_names()
    year_choices = [(r, r) for r in range(1920, date.today().year + 1)]
    year_choices.append((0,0))

    Vehicle_type = forms.ChoiceField(choices=vehicle_choices,
                                     label = "Vehicle Type",
                                     initial=5)
    Manufacturer_name = forms.ChoiceField(choices=manufacturer_names,
                                          label = "Manufacturer Name",
                                          initial=len(manufacturer_names)-1,
                                          )
    Color = forms.ChoiceField(choices=color_choices,
                              label="Color",
                              initial=len(color_choices)-1,
                              required=False)
    Year = forms.IntegerField(min_value=1920,
                                    max_value= date.today().year+1,
                                    label="Model Year",
                                    required=False)
    min_price = forms.DecimalField(decimal_places=2,
                                   label="Min Price",
                                   required=False,
                                   validators=[validate_decimals]
                                   )
    max_price = forms.DecimalField(decimal_places=2,
                                   label = "Max Price",
                                   required=False,
                                   validators=[validate_decimals])

    keywords = forms.CharField(label="Key Words",
                              required=False)

    def __init__(self, *args, **kwargs):

        super(QueryVehicleForm, self).__init__(*args, **kwargs)

        VIN = forms.CharField(min_length=1,max_length=17, required=False, label = "Search by VIN")
        sold_unsold_filter = forms.ChoiceField(choices=self.sold_unsold_options,label = "Filter by")

        user_role = os.environ["USER_ROLE"]

        if user_role in workers[0:2]:
            self.fields['sold_unsold_filter'] = sold_unsold_filter
            self.initial["sold_unsold_filter"] = "all"

        if user_role in workers:
            self.fields['VIN'] = VIN

    def extract_data(self):
        data = self.data.dict()
        data['Vehicle_type'] = self.vehicle_choices[int(data['Vehicle_type'])][1]
        data['Manufacturer_name'] = self.manufacturer_names[int(data['Manufacturer_name'])][1]
        data['Color'] = self.color_choices[int(data['Color'])][1]
        user_role = os.environ["USER_ROLE"]

        if user_role in workers[0:2]:
            data['sold_unsold_filter'] = self.sold_unsold_options[int(data['sold_unsold_filter'])][1]

        return data

class ReportTypes(forms.Form):
    report_choices = ((0, "Sales by Color"), (1, "Sales by Type"), (2, "Sales by Manufacturer"),
                   (3, "Gross Customer Income"), (4, "Average Time in Inventory"), (5, "Part Statistics"),
                     (6, "Below Cost Sales"), (7, "Repairs By Manufacturer/Type/Model"), (8, "Monthly Sales"),)
    reports = forms.ChoiceField(choices=report_choices)


    def extract_data(self):
        data = self.data.dict()
        data['reports'] = self.report_choices[int(data['reports'])][1]
        # data['Manufacturer_name'] = self.manufacturer_names[int(data['Manufacturer_name'])][1]
        # data['Color'] = self.color_choices[int(data['Color'])][1]
        # user_role = os.environ["USER_ROLE"]

        return data

class FilterBy(forms.Form):
   filter_choices = ((1, "Sold Vehicles"), (2, "Unsold Vehicles"), (3, "All Vehicles"),)
   filter = forms.ChoiceField(choices=filter_choices)

class LookupCustomer(forms.Form):
   drivers_licens_nr = forms.CharField(required=False)
   tin = forms.CharField(required=False)

   def extract_data(self):
       data = self.data.dict()
       return data

class AddCustomer(forms.Form):
  phone_number = forms.CharField()
  email = forms.EmailField(required = False,)
  street_address = forms.CharField()
  city = forms.CharField()
  state = forms.CharField()
  postal_code = forms.CharField()

  def __init__(self, *args, **kwargs):

      super(AddCustomer, self).__init__(*args, **kwargs)

      # Person Fields
      first_name = forms.CharField()
      last_name = forms.CharField()
      driver_license_nr = forms.CharField()
      person_fields = [first_name,last_name,driver_license_nr]
      person_names = ["first_name", "last_name", "driver_license_nr", "customer_id"]

      # Business Fields
      business_name = forms.CharField()
      contact_name = forms.CharField()
      contact_title = forms.CharField()
      TIN = forms.CharField()
      business_fields = [business_name,contact_name,contact_title,TIN]
      business_names = ["business_name", "contact_name", "contact_title", "TIN", "customer_id"]

      add_user_type = os.environ["ADD_USER_TYPE"] # can either be person or business

      if add_user_type == "individual":
          self.add_fields_to_form(person_fields,person_names)
      elif add_user_type == "business":
          self.add_fields_to_form(business_fields,business_names)



  def add_fields_to_form(self,form_list:list, name_list):
      for i in range(len(form_list)):

          self.fields[name_list[i]] = form_list[i]

  def clean_data(self):
        pass

  def extract_data(self):
      data:dict = self.data.dict()

      if "TIN" in data.keys():
          row_customer_type = [data["TIN"],data["contact_name"],data["contact_title"],data["business_name"]]
          customer_type = "business"
      else:
          row_customer_type = [data["driver_license_nr"],data["first_name"], data["last_name"]]
          customer_type = "person"

      row_customer = (data["phone_number"],data["email"],data["street_address"],data["city"],data["state"],data["postal_code"])

      return row_customer, row_customer_type, customer_type

class AddVehicle(forms.Form):
    VIN = forms.CharField()
    Year = forms.CharField()
    Model_name = forms.CharField()
    Description = forms.CharField()
    Invoice_price = forms.CharField()
    List_price = forms.CharField()
    Inventory_date = forms.CharField()
    Manufacturer_name = forms.CharField()
    Username = forms.CharField()

    def clean_data(self):
        pass

class AddRepair(forms.Form):
  VIN = forms.CharField()
  Customer_id = forms.CharField()
  Start_date = forms.DateField()
  Labor_charges = forms.CharField()
  Total_cost = forms.CharField()
  Description = forms.CharField()
  Completion_date = forms.DateField()
  Odometer_reading = forms.CharField()
  Username = forms.CharField()

class SellVehicle(forms.Form):

    def __init__(self,vin="None",invoice_price="none", *args, **kwargs):

        super(SellVehicle, self).__init__(*args, **kwargs)

        self.vin = vin
        self.invoice_price = invoice_price
        os.environ["SALES_INVOICE_PRICE"] = str(invoice_price)

        self.fields['VIN'] = forms.CharField(
            required=True,
            initial=self.vin,
        )
        self.fields['sales_person_username'] = forms.CharField(
            validators=[employee_lookup],
            required=True,
        )
        self.fields["licence_nr"] = forms.CharField(
            validators=[person_lookup],
            required=False
        )

        self.fields["TIN"] = forms.CharField(
            validators=[business_lookup],
            required=False
        )
        self.fields["sales_price"] = forms.DecimalField(
            decimal_places=2,
            label="Sales Price",
            required=True,
            validators=[validate_decimals, price_check])

        self.fields["sales_date"] = forms.DateTimeField(
            label="Sales date",
            initial=datetime.now(timezone_est),
            required=True,
            validators=[date_check])


    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('licence_nr') and not cleaned_data.get('TIN'):  # This will check for None or Empty
            raise ValidationError({'licence_nr': 'One of licence_nr or TIN should have a value.'})

    def extract_data(self):
        data = self.data.dict()

        if len(data["licence_nr"])>0:
            id = get_customer_id(data["licence_nr"], "licence_nr")
            print("person id is used",id)

        else:
            id = get_customer_id(data["TIN"], "TIN")
            print("business id is used",id)

        row = (data["VIN"],data["sales_person_username"],id,data["sales_price"],data["sales_date"])

        return row

class AddVehicleForm(forms.Form):
    '''
   TODO: right now color chices are hard coded
   we want to retrieve these with a query pass as parameter
   TODO: Vehicle type, manufacturer name, and model year, keyword is a drop down
   '''

    VIN = forms.CharField(required=True,validators=[check_vin_esitance])
    year = forms.IntegerField(min_value=1920,
                                    max_value= date.today().year+1,
                                    label="Model Year",
                                    required=True)
    model_name = forms.CharField(required=True)
    description = forms.CharField(label="Description", required=False)
    invoice_price = forms.DecimalField(decimal_places=2,
                                   label="Invoice Price",
                                   required=True,
                                   validators=[validate_decimals])

    inventory_date = forms.DateTimeField(
        label = "Inventory date",
        initial = datetime.now(timezone_est),
        required = True,
        validators = [date_check])
    manufacturer_name = forms.CharField(required=True)
    inventory_clerk_username = forms.CharField(
            validators=[employee_lookup],
            required=True,
        )

    colors = forms.CharField(help_text="ex: red,green",required = True)

    def __init__(self, *args, **kwargs):

        super(AddVehicleForm, self).__init__(*args, **kwargs)

        vehicle_type = os.environ["VEHICLE_TYPE"]
        print("Inform vehicle type: ", vehicle_type)
        if vehicle_type == "Car":
            self.fields["doors_ct"] = forms.IntegerField(required=True, min_value=1, max_value=6)
        elif vehicle_type == "Convertible":
            self.fields["roof_type"] = forms.CharField(required=True)
            self.fields["back_seat_ct"] = forms.IntegerField(required=True, min_value=0, max_value=8)
        elif vehicle_type == "Truck":
            self.fields["cargo_capacity"] = forms.FloatField(required=True, min_value=0.0)
            self.fields["cargo_cover_type"] = forms.CharField(required=False)
            self.fields["axle_ct"] = forms.IntegerField(required=True, min_value=2, max_value=8)
        elif vehicle_type == "VanMinivan":
            self.fields["driver_back_door"] = forms.BooleanField(required=True)
        elif vehicle_type == "SUV":
            self.fields["drive_train_type"] = forms.CharField(required=True)
            self.fields["cup_holder_ct"] = forms.IntegerField(required=True, min_value=0, max_value=20)

    def extract_data(self):
        data = self.data.dict()
        vehicle_type = os.environ["VEHICLE_TYPE"]
        VIN = data["VIN"]

        manufacturer_row = [data["manufacturer_name"]]
        vehicle_row = [VIN,data["year"],data["model_name"],data["description"],data["invoice_price"],
                        data["inventory_date"],data["manufacturer_name"],data["inventory_clerk_username"]]

        color_data = [(VIN,color) for color in data["colors"].split(",")]

        car_type_dict = {"type":vehicle_type,"data":[VIN]}

        if vehicle_type == "Car":
            doors_ct = data["doors_ct"]
            car_type_dict["data"].append(doors_ct)

        elif vehicle_type == "Convertible":
            roof_type = data["roof_type"]
            back_seat_ct = data["back_seat_ct"]
            car_type_dict["data"].extend([roof_type,back_seat_ct])

        elif vehicle_type == "Truck":
            cargo_capacity = data["cargo_capacity"]
            cargo_cover_type = data["cargo_cover_type"]
            axle_ct = data["axle_ct"]
            car_type_dict["data"].extend([cargo_capacity, cargo_cover_type,axle_ct])

        elif vehicle_type == "VanMinivan":
            drive_back_door = data["drive_back_door"]
            car_type_dict["data"].append(drive_back_door)

        elif vehicle_type == "SUV":
            drive_train_type = data["drive_train_type"]
            cup_holder_ct = data["cup_holder_ct"]
            car_type_dict["data"].extend([drive_train_type, cup_holder_ct])

        car_type_dict["data"] = tuple(car_type_dict["data"])

        return tuple(manufacturer_row),tuple(vehicle_row),car_type_dict,color_data

class SelectVehicleTypeForm(forms.Form):
    '''
   TODO: right now color chices are hard coded
   we want to retrieve these with a query pass as parameter
   TODO: Vehicle type, manufacturer name, and model year, keyword is a drop down
   '''

    vehicle_type = os.getenv("VEHICLE_TYPE","Car")
    print(vehicle_type)
    vehicle_choices = [(0, "Car"), (1, "Convertible"), (2, "SUV"), (3, "Truck"), (4, "VanMinivan")]

    initial_choice = [car[0] for car in vehicle_choices if car[1] == "Car"][0]

    vehicle_type = forms.ChoiceField(choices=vehicle_choices,
                                                    label="Vehicle Type",
                                                    initial=initial_choice)

    def extract_data(self):
        data = self.data.dict()
        vehicle_type_selected = self.vehicle_choices[int(data['vehicle_type'])][1]

        return vehicle_type_selected

class AddPartForm(forms.Form):
    '''
   TODO: right now color chices are hard coded
   we want to retrieve these with a query pass as parameter
   TODO: Vehicle type, manufacturer name, and model year, keyword is a drop down
   '''

    vehicle_type = os.getenv("VEHICLE_TYPE","Car")
    print(vehicle_type)
    vehicle_choices = [(0, "Car"), (1, "Convertible"), (2, "SUV"), (3, "Truck"), (4, "VanMinivan")]

    initial_choice = [car[0] for car in vehicle_choices if car[1] == "Car"][0]

    vehicle_type = forms.ChoiceField(choices=vehicle_choices,
                                                    label="Vehicle Type",
                                                    initial=initial_choice)

    def extract_data(self):
        data = self.data.dict()
        vehicle_type_selected = self.vehicle_choices[int(data['vehicle_type'])][1]

        return vehicle_type_selected

class AddRepairForm(forms.Form):
    '''
   TODO: right now color chices are hard coded
   we want to retrieve these with a query pass as parameter
   TODO: Vehicle type, manufacturer name, and model year, keyword is a drop down
   '''

    vehicle_type = os.getenv("VEHICLE_TYPE","Car")
    print(vehicle_type)
    vehicle_choices = [(0, "Car"), (1, "Convertible"), (2, "SUV"), (3, "Truck"), (4, "VanMinivan")]

    initial_choice = [car[0] for car in vehicle_choices if car[1] == "Car"][0]

    vehicle_type = forms.ChoiceField(choices=vehicle_choices,
                                                    label="Vehicle Type",
                                                    initial=initial_choice)

    def extract_data(self):
        data = self.data.dict()
        vehicle_type_selected = self.vehicle_choices[int(data['vehicle_type'])][1]

        return vehicle_type_selected

class ViewEditRepairForm(forms.Form):
    '''
   TODO: right now color chices are hard coded
   we want to retrieve these with a query pass as parameter
   TODO: Vehicle type, manufacturer name, and model year, keyword is a drop down
   '''

    vehicle_type = os.getenv("VEHICLE_TYPE","Car")
    print(vehicle_type)
    vehicle_choices = [(0, "Car"), (1, "Convertible"), (2, "SUV"), (3, "Truck"), (4, "VanMinivan")]

    initial_choice = [car[0] for car in vehicle_choices if car[1] == "Car"][0]

    vehicle_type = forms.ChoiceField(choices=vehicle_choices,
                                                    label="Vehicle Type",
                                                    initial=initial_choice)

    def extract_data(self):
        data = self.data.dict()
        vehicle_type_selected = self.vehicle_choices[int(data['vehicle_type'])][1]

        return vehicle_type_selected