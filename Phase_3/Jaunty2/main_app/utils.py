from .runtime_constants import SERVER
import getpass
import os

'''
TODO:
1. Update the generate_query function to handle SELCET, DELETE, UPDATE, INSERT
2. Create a folder with all report or long queries in text files
3. Create a function that reads the queries from text files and returns string

'''

from typing import Tuple, List
import pyodbc

def find_customer(Driver_license,Tin):
    data = []
    header = []

    if Driver_license == "" and Tin == "":
        status = "At least one (driver's license or TIN) must be entered to look up customer."
    elif Driver_license != "":
        query = f"SELECT * FROM Person WHERE Driver_license = {Driver_license}"
        data, header = run_query(query)  # run query
        if len(data) == 0:
            header = []
            status = "Person not found, please add customer to the database."
        else:
            status = "Person found in the customer registry. Details below."
    elif Tin != "":
        query = f"SELECT * FROM Business WHERE Tin = {Tin}"
        data, header = run_query(query)  # run query
        if len(data) == 0:
            header = []
            status = "Business not found, please add customer to the database."
        else:
            status = "Business found in the customer registry. Details below."
    else:
        status = "Logic not captured by the code."

    return data, header, status

def compose_pyodbc_connection():
    connection_string = 'Driver={SQL Server};Server=%s;Database=CS6400;Trusted_Connection=yes;' % ( SERVER )
    if os.getenv("PYODBC_AUTH")=="True":
        usr = os.getenv("PYODBC_USER")
        pw = os.getenv("PYODBC_PW")
        connection_string+='uid=%s;pwd=%s;'%(usr,pw)

    return connection_string

def gen_query_add_row(table_name:str,row:tuple)->str:
    colQuery = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table_name}';"

    colnames,_ = run_query(colQuery)

    colnames = ','.join([col[0] for col in colnames])
    row_len = len(row)

    row =",".join(["?" for i in range(row_len)])
    query = f"INSERT INTO {table_name}({colnames}) VALUES ({row}) "
    return query

def get_search_vehicle_query(user_input:dict)->str:
    '''
    :param user_input: dictionary of form {col1:value,col2:value}
    :return:

    TODO: format query per project structure
    '''

    query = get_query_from_file("query_vehicle.txt")

    vehicle_fields = ["Manufacturer_name","Year","VIN","Vehicle_type","Model_name"]

    where_clause = []
    for key, val in user_input.items():

        if (val != "all") and (val != ""):
            if key in vehicle_fields:
                if key == "VIN":
                    where_clause.append(f"(v.VIN='{val}')")
                else:
                    where_clause.append(f"({key}='{val}')")

            if key == "min_price":
                where_clause.append(f"(List_price > {user_input['min_price']})")
            if key == "max_price":
                where_clause.append(f"(List_price < {user_input['max_price']})")

            if val == "sold": # for sold unsold filter
                where_clause.append(f"(v.VIN IN ( SELECT s.VIN FROM Sale s))")
            elif val == "unsold":
                where_clause.append(f"(v.VIN NOT IN ( SELECT s.VIN FROM Sale s))")

            if key == "Color":
                where_clause.append(f"((SELECT DISTINCT STRING_AGG(c.Color,' | ') FROM Color c WHERE c.VIN=v.VIN) LIKE '%{val}%')")

            if key == "keywords":
                keywords = user_input["keywords"].split(',')
                for word in keywords:
                    where_clause.append(f"(Description LIKE '%{word}%')")

    if len(where_clause) > 0:
        query += " WHERE "
        query += " AND ".join(where_clause)
    query += " ORDER BY VIN ASC"
    return query

def cleanup_null_cols(row:tuple,columns:list):
    """
    Function will clean up a row that has null values and remove columsn with null values

    :param row:
    :param columns:
    :return:
    """
    row_vals = []
    cols = []

    for i in range(len(row)):
        if row[i] is not None:
            row_vals.append(row[i])
            cols.append(columns[i])

    assert len(row_vals)==len(cols)

    return tuple(row_vals),cols

def run_query(query:str,return_results:bool = True)->List[tuple]:
    '''
    :param query:
    :return:
    '''
    connection_str = compose_pyodbc_connection()
    conn = pyodbc.connect(connection_str)
    cursor = conn.cursor()
    cursor.execute(query)

    results:List[tuple] = None
    header:List[str] = None
    if return_results:
        results = cursor.fetchall()
        header = [column[0] for column in cursor.description]

    cursor.close()
    return results, header

def insert_row(query:str,row):
    '''
    :param query:
    :return:
    '''

    connection_str = compose_pyodbc_connection()
    conn = pyodbc.connect(connection_str)

    cursor = conn.cursor()
    cursor.execute(query,row)
    conn.commit()
    cursor.close()

    return

def get_colors():
    query = "SELECT DISTINCT Color FROM Color"
    colors, cols = run_query(query)
    colors = [(i, colors[i][0]) for i in range(len(colors))]
    colors.append((len(colors), "all"))
    return colors

def get_query_from_file(file_name:str)->str:
    cwd = os.getcwd()
    sql_path = os.path.join(cwd,"main_app\SQL")
    file_path = os.path.join(sql_path,file_name)

    with open(file_path, 'r') as file:
        query_string = file.read().replace('\n', ' ').replace('\t',' ')
        query_string = query_string.replace("  "," ").replace("   "," ")
    return query_string

def get_manufacturer_names():
    query = "select DISTINCT Manufacturer_name from Manufacturer"
    manufacturers, cols = run_query(query)
    manufacturers = [(i, manufacturers[i][0]) for i in range(len(manufacturers))]
    manufacturers.append((len(manufacturers), "all"))
    return manufacturers

def add_repair(user_input):
    #query = get_query_from_file("add_repair.txt")

    repair_fields = ["VIN", "Customer Id", "Start_date", "Labor_charges", "Total_cost", "Description",
                     "Completion_date", "Odometer_reading", "Username"]
    row_tuple = []
    for key, val in user_input.items():

        if (val != "all") and (val != ""):
            if key in repair_fields:
                if key == "VIN":
                    row_tuple.append(f"(v.VIN='{val}')")


            if key == "Customer Id":
                where_clause.append(f"(List_price > {user_input['min_price']})")
            if key == "max_price":
                where_clause.append(f"(List_price < {user_input['max_price']})")

            if val == "sold":  # for sold unsold filter
                where_clause.append(f"(v.VIN IN ( SELECT s.VIN FROM Sale s))")
            elif val == "unsold":
                where_clause.append(f"(v.VIN NOT IN ( SELECT s.VIN FROM Sale s))")

            if key == "Color":
                where_clause.append(
                    f"((SELECT DISTINCT STRING_AGG(c.Color,' | ') FROM Color c WHERE c.VIN=v.VIN) LIKE '%{val}%')")

            if key == "keywords":
                keywords = user_input["keywords"].split(',')
                for word in keywords:
                    where_clause.append(f"(Description LIKE '%{word}%')")





    query = gen_query_add_row("Repair", user_input)
    return query




def run_reports(user_input):

    # $MaxSaleDate = "SELECT MAX(Sale_date)from Sale"

    report_fields = ["Sales by Color", "Sales by Type", "Sales by Manufacturer", "Gross Customer Income",
                     "Average Time in Inventory", "Part Statistics", "Below Cost Sales",
                     "Repairs By Manufacturer/Type/Model", "Monthly Sales"]


    for key, val in user_input.items():

        # if (val != "all") and (val != ""):
        if val in report_fields:
            if val == "Sales by Color":
                query = get_query_from_file("sale_by_color.txt")
                # print(query)
                return query

            if val == "Sales by Type":
                query = get_query_from_file("sale_by_type.txt")
                return query

            if val == "Sales by Manufacturer":
                query = get_query_from_file("sale_by_manufacturer.txt")
                return query

            if val == "Gross Customer Income":
                query = get_query_from_file("gross_customer_income.txt")
                return query

            if val == "Average Time in Inventory":
                query = get_query_from_file("avg_time_in_inventory.txt")
                return query

            if val == "Part Statistics":
                query = get_query_from_file("part_statistics.txt")
                return query

            if val == "Below Cost Sales":
                query = get_query_from_file("below_cost_sales.txt")
                return query

            if val == "Repairs By Manufacturer/Type/Model":
                query = get_query_from_file("repairs_by_manufacturer_type_model.txt")
                return query

            if val == "Monthly Sales":
                query = get_query_from_file("monthly_sales.txt")
                return query





def add_customer_query(user_input:dict)->str:
    '''
    :param user_input: dictionary of form {col1:value,col2:value}
    :return:

    TODO: format query per project structure
    '''

    add_user_type = os.environ["ADD_USER_TYPE"]


    for key, val in user_input.items():

        if add_user_type == "individual":
            query = gen_query_add_row('Person', )
            return query




    return query

def get_detailed_vehicle_query(vin: str):
    user_role = os.environ["USER_ROLE"]

    if user_role not in ["manager","owner"]:
        query_addition = f" AND v.VIN = '{vin}';"
    else:
        query_addition = f" v.VIN = '{vin}';"


    if user_role in ["manager","owner"]:
        query = get_query_from_file("vehicle_detailed_manager.txt")

    elif user_role == "inventory_clerk":
        print("getting query for ivc")
        query = get_query_from_file("vehicle_detailed_inventory_clerk.txt")

    elif user_role in ["sales_person","service_writer"]:
        query = get_query_from_file("vehicle_detailed_worker.txt")

    else:
        query = get_query_from_file("vehicle_detailed_regular.txt")

    return query+query_addition

def get_sales_query(vin:str):
    query_addition = f" WHERE s.VIN IS NOT NULL AND s.VIN = '{vin}';"
    query = get_query_from_file("vehicle_detailed_sales.txt")
    return query+query_addition

def get_repair_query(vin:str):
    query_addition = f" WHERE r.VIN IS NOT NULL AND r.VIN = '{vin}';"
    query = get_query_from_file("vehicle_detailed_repair.txt")
    return query+query_addition

def get_data_for_template(vin:str,query_type:str):
    # for repairs details
    print("getting data for: ", query_type)

    if query_type == "vehicle":
        query = get_detailed_vehicle_query(vin)
    elif query_type == "sales":
        query = get_sales_query(vin)
    elif query_type == "repair":
        query = get_repair_query(vin)

    data, cols = run_query(query)

    if len(data) > 0:
        data, cols = cleanup_null_cols(data[0], cols)
        status = ""
    elif (len(data) == 0) and (query_type == "vehicle"):
        cols = []
        status = "The vehicle is no longer in inventory because it was sold."
    else:
        cols = []
        status = "No results found for: "+query_type

    return {'header':cols, 'data':data, "status":status}
