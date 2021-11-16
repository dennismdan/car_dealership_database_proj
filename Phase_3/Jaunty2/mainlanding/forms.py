from django import forms

'''
Pass forms to html
https://djangobook.com/mdj2-django-forms/

Dynamic Forms: 
https://www.b-list.org/weblog/2008/nov/09/dynamic-forms/
'''

class LoginForm(forms.Form):
   user = forms.CharField(max_length = 100)
   password = forms.CharField(widget = forms.PasswordInput())



class QueryVehicleForm(forms.Form):
   color_choices = ((1,"green"),(2,"blue"),(3,"black"),(4,"white"))
   vehicle_type = forms.CharField(max_length = 100)
   manufacturer_name = forms.CharField()
   model_year = forms.DateField()
   color = forms.ChoiceField(choices=color_choices)
   list_price = forms.CharField()
   keywords = forms.CharField(max_length = 100)


class ReportTypes(forms.Form):
   report_choices = ((1, "Sales by month"), (2, "sales by vehicle"), (3, "sales by ..."), (4, "TODO: implement actual options"))
   reports = forms.ChoiceField(choices=report_choices)
