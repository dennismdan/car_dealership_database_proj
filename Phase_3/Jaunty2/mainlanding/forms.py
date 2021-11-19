from django import forms

'''
Pass forms to html
https://djangobook.com/mdj2-django-forms/

Dynamic Forms: 
https://www.b-list.org/weblog/2008/nov/09/dynamic-forms/

TODO: apply business constraints   
'''

class LoginForm(forms.Form):
   user = forms.CharField(max_length = 100)
   password = forms.CharField(widget = forms.PasswordInput())



class QueryVehicleForm(forms.Form):
   '''
   TODO: right now color chices are hard coded
   we want to retrieve these with a query pass as parameter
   TODO: Vehicle type, manufacturer name, and model year, keyword is a drop down
   '''

   color_choices = ((1,"green"),(2,"blue"),(3,"black"),(4,"white"))

   vehicle_type = forms.CharField()
   manufacturer_name = forms.CharField()
   model_year = forms.DateField()
   color = forms.ChoiceField(choices=color_choices)
   list_price = forms.FloatField()
   keywords = forms.CharField()

   def clean_data(self):
      pass




class ReportTypes(forms.Form):
   report_choices = ((1, "Sales by month"), (2, "sales by vehicle"), (3, "sales by ..."), (4, "TODO: implement actual options"))
   reports = forms.ChoiceField(choices=report_choices)



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

