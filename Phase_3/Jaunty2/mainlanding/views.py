from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import LoginForm, QueryVehicleForm,ReportTypes

def home(request):
    view_inventory = False
    if request.method == 'POST':
        form = QueryVehicleForm(request.POST)
        print(form)
        if form.is_valid():
            return HttpResponseRedirect('/home?view_inventory=True')
        else:
            form = QueryVehicleForm()
            if 'view_inventory' in request.GET:
                view_inventory = True
                data = "TODO: run query function here to get data "
    else:
        print("form same as before")
        form = QueryVehicleForm()
    return render(request,'mainlanding/home.html',
                  {'form': form,
                   'view_inventory': view_inventory,
                   'data':"None"})


def base(request):
    print("base")
    return render(request, 'mainlanding/base.html')

def add_vehicle(request):
    print("add_vehicle")
    return render(request, 'mainlanding/add_vehicle.html')

def reports(request):
    print("reports")
    form = ReportTypes()
    return render(request, 'mainlanding/reports.html',{'form': form})

def repairs(request):
    print("repairs")
    return render(request, 'mainlanding/repairs.html')

def click(request):
    print("clicked")
    return render(request, 'mainlanding/clicked.html')

def login(request):
    return render(request, 'mainlanding/loging.html')



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