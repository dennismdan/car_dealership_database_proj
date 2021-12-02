import os

if os.getenv("VEHICLE_TYPE") is None:
    os.environ["VEHICLE_TYPE"] = "Car"

if os.getenv("USER_ROLE") is None:
    os.environ["USER_ROLE"] = "owner"

if os.getenv("ADD_USER_TYPE") is None:
    os.environ["ADD_USER_TYPE"] = "individual"

if os.getenv("SALES_VIN") is None:
    os.environ["SALES_VIN"] = '0'

if os.getenv("SALES_INVOICE_PRICE") is None:
    os.environ["SALES_INVOICE_PRICE"] = '0.00'



