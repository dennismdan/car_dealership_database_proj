import os

from django import forms
import main_app.views

from django.core.exceptions import ValidationError
from main_app.utils import get_colors,get_manufacturer_names,run_reports
import datetime
import os

workers = ["owner","manager","inventory_clerk","sales_person","service_writer"] # only role "regular_user" missing

'''
Pass forms to html
https://djangobook.com/mdj2-django-forms/

Dynamic Forms: 
https://www.b-list.org/weblog/2008/nov/09/dynamic-forms/

TODO: apply business constraints   
'''


class LoginForm(forms.Form):
    user = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())

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
    year_choices = [(r, r) for r in range(1920, datetime.date.today().year + 1)]
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
                                    max_value=datetime.date.today().year,
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
   drivers_licens_nr = forms.IntegerField(required=False)
   tin = forms.IntegerField(required=False)

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
      customer_id = forms.CharField()
      person_fields = [first_name,last_name,driver_license_nr,customer_id]
      person_names = ["first_name", "last_name", "driver_license_nr", "customer_id"]

      # Business Fields
      business_name = forms.CharField()
      contact_name = forms.CharField()
      contact_title = forms.CharField()
      TIN = forms.CharField()
      customer_id = forms.CharField()
      business_fields = [business_name,contact_name,contact_title,TIN,customer_id]
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
    VIN = forms.CharField()
    Year = forms.CharField()
    Model_name = forms.CharField()
    Description = forms.CharField()
    Invoice_price = forms.CharField()
    List_price = forms.CharField()
    Inventory_date = forms.CharField()
    Manufacturer_name = forms.CharField()
    Username = forms.CharField()
