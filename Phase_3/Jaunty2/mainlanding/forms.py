from django import forms
from .utils import get_colors
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



class QueryVehicleForm(forms.Form):
   '''
   TODO: right now color chices are hard coded
   we want to retrieve these with a query pass as parameter
   TODO: Vehicle type, manufacturer name, and model year, keyword is a drop down
   '''
   color_choices = get_colors()
   vehicle_type = forms.CharField()
   manufacturer_name = forms.CharField()
   model_year = forms.DateField()
   color = forms.ChoiceField(choices=color_choices)
   list_price = forms.FloatField()
   keywords = forms.CharField()




class ReportTypes(forms.Form):
   report_choices = ((1, "Sales by Color"), (2, "Sales by Type"), (3, "Sales by Manufacturer"),
                     (4, "Gross Customer Income"), (5, "Average Time in Inventory"), (6, "Part Statistics"),
                     (7, "Below Cost Sales"), (8, "Repairs By Manufacturer/Type/Model"), (9, "Monthly Sales"),)
   reports = forms.ChoiceField(choices=report_choices)


class FilterBy(forms.Form):
   filter_choices = ((1, "Sold Vehicles"), (2, "Unsold Vehicles"), (3, "All Vehicles"),)
   filter = forms.ChoiceField(choices=filter_choices)


class LookupCustomer(forms.Form):
   drivers_licens_nr = forms.IntegerField()
   tin = forms.IntegerField()


class AddCustomer(forms.Form):
  phone_number = forms.CharField()
  email = forms.EmailField(required = False,)
  street_address = forms.CharField()
  city = forms.CharField()
  state = forms.CharField()
  postal_code = forms.CharField()

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
