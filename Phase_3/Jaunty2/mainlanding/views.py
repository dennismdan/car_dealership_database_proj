from django.shortcuts import render
from django.http import HttpResponse


def home(request):

    colnames = ("model","vin")

    data = [("toyota",1234),("jeep",543)]

    user_expressions = [{"name":"zee", "says":"yayyy"},
                       {"name":"tanweer", "says":"wohooo"},
                       {"name":"Maruciou", "says":"yahooo"}]

    context = {"user_exprssions":user_expressions,
               "table":{
                   "colnames":colnames,
                   "data":data
                    }
               }

    return render(request, 'mainlanding/home.html',context)


def click_button(request):
    print("clicked")

    return HttpResponse("<h1>Button Clicked</h1>")




