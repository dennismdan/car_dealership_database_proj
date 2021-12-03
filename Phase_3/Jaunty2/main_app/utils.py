from .runtime_constants import SERVER
import getpass
import os


from typing import Tuple, List, Dict
import pyodbc
from datetime import datetime

def gen_query_update_row(table_name: str,
                         update_fields: dict,
                         where_fields: dict ) -> str:
    set_clause = ", ".join([f"{key} = '{val}'" for key,val in update_fields.items() if val not in [None,""]])
    where_clause = " AND ".join([f"{key} = '{val}'" for key, val in where_fields.items()])

    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"
    print("Update row query: ", query)
    return query

def update_row(query: str):
    """
    :param query: string type for example 'UPDATE Table SET col=val ...'
    :return:
    """
    try:
        connection_str = compose_pyodbc_connection()
        conn = pyodbc.connect(connection_str)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        status = "Updated row successfully!"
        message_class = "success"
    except Exception as e:
        print(e)
        status = "Issue when updating row."
        message_class = "error"

    return status, message_class

def update_table(query: str):
    """
    :param query:
    :return:
    """
    print("Update table query: ", query)
    try:
        connection_str = compose_pyodbc_connection()
        conn = pyodbc.connect(connection_str)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        status = "Updated table successfully!"
        message_class = "success"
    except Exception as e:
        print(e)
        status = "Issue when updating row."
        message_class = "error"

    return status, message_class

def stage_repair_data(row_dict, edit_allowed ):
    query = get_query_with_condition(table_name="Repair",
                                     select_cols=[],
                                     where_clause=row_dict)
    results, cols = run_query(query)
    if results:
        results = results[0]
        data = {cols[i]:results[i] for i in range(len(cols))}
        status = "Found repair"
        css_class = "success"
    else:
        data = {cols[i]: "" for i in range(len(cols))}
        status = "Did not find any repairs. \n"\
                 "Please add a new repair."
        css_class = "error"

    if edit_allowed and results:
        edit_cols = ["Completion_date", "Labor_charges"]
    else:
        edit_cols = []

    return data, edit_cols, status,css_class

def is_repair_complete(repair_key_fields:dict)->bool:
    """
    :param repair_key_fields: {"VIN":vin,"Customer_id":Customer_id,"Start_date":Start_date}
    :return: True/False indicating if a repair is complete
    """
    where_clause = " AND ".join([f"{k} = '{v}'" for k, v in repair_key_fields.items()])
    query = "SELECT Completion_date,Labor_charges,Total_cost FROM Repair WHERE " + where_clause
    row = run_query(query)[0]
    if row:
        row = row[0]
    else:
        return False

    complete = []

    for val in row:
        if val in ["",None]:
            complete.append(False)
        else:
            complete.append(True)

    print("inside repair complete: ", all(complete))
    return all(complete)

def repair_start_date_is_unique(vin:str,start_date:datetime)->bool:
    """
    :param vin:
    :param start_date:
    :return:
    """
    query = f"SELECT * FROM Repair WHERE VIN = '{vin}' AND Start_date = '{start_date}'"
    results = run_query(query)[0]

    return len(results) == 0

def repair_starts_before_ends(Start_date: datetime,
                              Completion_date: datetime) -> bool:
    if Completion_date in [None, ""]:
        result = True
    else:
        result = Start_date <= Completion_date
    return result

def get_customer_id(customer_unique_nr, customer_type):
    if customer_type == "licence_nr":
        from_clause = "Person"
        where_clause = "Driver_license"
    elif customer_type == "TIN":
        from_clause = "Business"
        where_clause = "TIN"
    else:
        return ""

    if customer_unique_nr == "":
        return ""

    else:
        query = f"SELECT Customer_id FROM {from_clause} WHERE {where_clause} = '{customer_unique_nr}'"
        data, _ = run_query(query)  # run query

        if len(data) == 0:
            return ""
        else:
            return data[0][0]


def check_if_instance_exists(table_name: str,
                             select_cols: List[str],
                             where_clause: List[tuple]) -> bool:
    """

    :param table_name:
    :param select_cols:
    :param where_clause: ex [(col1,val1),(col2,val2)...]
    :return:
    """
    if len(select_cols) == 0:
        columns = " * "
    else:
        columns = ", ".join(select_cols)

    where = " AND ".join([pair[0] + " = " + f"'{str(pair[1])}'" for pair in where_clause])

    query = f"SELECT " + columns + " FROM " + table_name + " WHERE " + where

    results, _ = run_query(query)

    if len(results) > 0:
        return True
    else:
        return False

def get_query_with_condition(table_name: str,
                             select_cols: List[str],
                             where_clause: dict) -> str:
    """
    :param table_name:
    :param select_cols:
    :param where_clause: ex [(col1,val1),(col2,val2)...]
    :return:
    """
    if len(select_cols) == 0:
        columns = " * "
    else:
        columns = ", ".join(select_cols)

    where = " AND ".join([f"{k} = '{v}'" for k, v in where_clause.items()])

    query = f"SELECT " + columns + " FROM " + table_name + " WHERE " + where

    return query


def find_customer(Driver_license, Tin):
    data = []
    header = []

    if Driver_license == "" and Tin == "":
        status = "At least one (driver's license or TIN) must be entered to look up customer."
    elif Driver_license != "":
        query = f"SELECT * FROM Person WHERE Driver_license = '{Driver_license}'"
        data, header = run_query(query)  # run query
        if len(data) == 0:
            header = []
            status = "Person not found, please add customer to the database."
        else:
            status = "Person found in the customer registry. Details below."
    elif Tin != "":
        query = f"SELECT * FROM Business WHERE TIN = '{Tin}'"
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
    connection_string = 'Driver={SQL Server};Server=%s;Database=CS6400;Trusted_Connection=yes;' % (SERVER)
    if os.getenv("PYODBC_AUTH") == "True":
        usr = os.getenv("PYODBC_USER")
        pw = os.getenv("PYODBC_PW")
        connection_string += 'uid=%s;pwd=%s;' % (usr, pw)

    return connection_string


def gen_query_add_row(table_name: str, row: tuple, skip_col_list: list = []) -> str:
    colQuery = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table_name}';"

    colnames, _ = run_query(colQuery)

    colnames = [col[0] for col in colnames]

    if len(skip_col_list) > 0:
        print("skipping cols")
        new_cols = []
        for col in colnames:
            if col in skip_col_list:
                print(col)
                continue
            new_cols.append(col)

        colnames = new_cols


    colnames = ','.join(colnames)

    row_len = len(row)

    row = ",".join(["?" for i in range(row_len)])
    query = f"INSERT INTO {table_name}({colnames}) VALUES ({row}) "
    print("Insert row query: ", query)

    return query


def get_search_vehicle_query(user_input: dict) -> str:
    '''
    :param user_input: dictionary of form {col1:value,col2:value}
    :return:
    '''

    query = get_query_from_file("query_vehicle.txt")

    vehicle_fields = ["Manufacturer_name", "Year", "VIN", "Vehicle_type", "Model_name"]

    print("User inputs: ", user_input)
    print("Query : ", query)

    if "sold_unsold_filter" in user_input:
        if user_input["sold_unsold_filter"] == "all":
            where_clause = []
        elif user_input["sold_unsold_filter"] == "unsold":
            where_clause = [" v.VIN NOT IN ( SELECT s.VIN FROM Sale s) "]
        elif user_input["sold_unsold_filter"] == "sold":
            where_clause = [" v.VIN IN ( SELECT s.VIN FROM Sale s) "]
    else:
        where_clause = [" v.VIN NOT IN ( SELECT s.VIN FROM Sale s) "]

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

            if key == "Color":
                where_clause.append(
                    f"((SELECT DISTINCT STRING_AGG(c.Color,' | ') FROM Color c WHERE c.VIN=v.VIN) LIKE '%{val}%')")

            if key == "keywords":
                where_clause.append(f"(Description LIKE '%{user_input['keywords']}%' OR manufacturer_name LIKE '%{user_input['keywords']}%' OR year LIKE '%{user_input['keywords']}%' OR model_name LIKE '%{user_input['keywords']}%')")
                # keywords = user_input["keywords"].split(',')
                # for word in keywords:
                #     where_clause.append(f"(Description LIKE '%{word}%')")


    if len(where_clause) > 0:
        query += " WHERE "+" AND ".join(where_clause)
    query += " ORDER BY VIN ASC"

    return query


def cleanup_null_cols(data: tuple, columns: list):
    """
    Function will clean up a row that has null values and remove columsn with null values

    :param row:
    :param columns:
    :return:
    """
    new_data = []
    cols = []

    col_idx = []

    for i in range(len(data[0])):
        col_has_good_vals = []
        for j in range(len(data)):
            col_has_good_vals.append(data[j][i] is not None)
        if any(col_has_good_vals):
            col_idx.append(i)
            cols.append(columns[i])

    for row in data:
        new_row = []
        for col_index in col_idx:
            new_row.append(row[col_index])
        new_data.append(tuple(new_row))

    assert len(new_data[0]) == len(cols)

    return new_data, cols


def run_query(query: str, return_results: bool = True) -> List[tuple]:
    '''
    :param query:
    :return:
    '''
    connection_str = compose_pyodbc_connection()
    conn = pyodbc.connect(connection_str)
    cursor = conn.cursor()

    cursor.execute(query)

    results: List[tuple] = None
    header: List[str] = None
    if return_results:
        results = cursor.fetchall()
        header = [column[0] for column in cursor.description]

    cursor.close()
    return results, header


def insert_row(query: str, row):
    """
    :param query: string type for example 'SELECT * FROM ...'
    :param row: is a tuple of values, for example, (val1,val2, val3...)
    :return:
    """
    try:
        connection_str = compose_pyodbc_connection()
        conn = pyodbc.connect(connection_str)
        cursor = conn.cursor()
        cursor.execute(query, row)
        conn.commit()
        cursor.close()
        status = "Row Added"
        message_class = "success"
    except Exception as e:
        print(e)
        status = "Issue adding a new row, could be that it already exists."
        message_class = "error"

    return status, message_class


def get_colors():
    query = "SELECT DISTINCT Color FROM Color"
    colors, cols = run_query(query)
    colors = [(i, colors[i][0]) for i in range(len(colors))]
    colors.append((len(colors), "all"))
    return colors


def get_query_from_file(file_name: str) -> str:
    cwd = os.getcwd()
    sql_path = os.path.join(cwd, "main_app\SQL")
    file_path = os.path.join(sql_path, file_name)

    with open(file_path, 'r') as file:
        query_string = file.read().replace('\n', ' ').replace('\t', ' ')
        query_string = query_string.replace("  ", " ").replace("   ", " ")
    return query_string


def get_manufacturer_names():
    query = "select DISTINCT Manufacturer_name from Manufacturer"
    manufacturers, cols = run_query(query)
    manufacturers = [(i, manufacturers[i][0]) for i in range(len(manufacturers))]
    manufacturers.append((len(manufacturers), "all"))
    return manufacturers


def add_repair(user_input):
    # query = get_query_from_file("add_repair.txt")

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

def get_monthly_sales_drilldown_query(year, month):

    query = f"SELECT TOP 1  \
           eu.First_name + ' ' + eu.Last_name AS SalesPersonName, \
           COUNT(s.Username) NumberVehiclesSold, \
           YEAR(s.Sale_date) AS SaleYear \
           ,MONTH(s.Sale_date) AS SaleYear \
           ,CAST(SUM(s.Sale_price) AS numeric (16,2)) TotalSales \
           FROM Sale s \
           LEFT JOIN EmployeeUser eu ON s.Username = eu.Username \
           WHERE YEAR(s.Sale_date) = {year} AND MONTH(s.Sale_date) = {month} \
           GROUP BY eu.First_name + ' ' + eu.Last_name, YEAR(s.Sale_date) ,MONTH(s.Sale_date) \
           ORDER BY NumberVehiclesSold DESC, TotalSales DESC"

    return query


def get_data_for_template_report(year,month):

    query = get_monthly_sales_drilldown_query(year, month)
    data, cols = run_query(query)

    return {'header':cols, 'data':data}


def gross_customer_drilldown_sales_query(Customer_id):
    query = f"SELECT CP.CustomerName,s.Sale_date,\
            CAST(s.Sale_price AS numeric(16,2))AS Sale_price,s.VIN,v.Year,v.Manufacturer_name,v.Model_name, \
            eu.First_name + ' ' + eu.Last_name AS SalesPersonName \
            FROM Customer c \
            LEFT JOIN (SELECT p.Customer_id, (p.First_name + ' ' + p.Last_name)as CustomerName FROM Person p \
            UNION \
            SELECT b.Customer_id, b.Business_name as CustomerName FROM Business b) AS  CP\
            ON c.Customer_id = CP.Customer_id \
            LEFT JOIN Sale s ON c.Customer_id = s.Customer_id \
            LEFT JOIN Vehicle v ON s.VIN = v.VIN \
            LEFT JOIN EmployeeUser eu ON s.Username = eu.Username \
            WHERE c.Customer_id = {Customer_id} \
            ORDER BY s.Sale_date DESC, s.VIN DESC"

    return query


def gross_customer_drilldown_repair_query(Customer_id):
    query = f"SELECT \
            CP.CustomerName, r.Start_date, r.Completion_date, r.VIN, r.Odometer_reading, CAST(r.Labor_charges AS numeric(16,2)) AS Labor_Charges, \
            CAST(r.Total_cost AS numeric(16,2)) AS Total_cost, eu.First_name + ' ' + eu.Last_name AS SalesPersonName \
            FROM Customer c LEFT JOIN(SELECT p.Customer_id, (p.First_name + ' ' + p.Last_name)as CustomerName \
            FROM Person p  \
            UNION  \
            SELECT b.Customer_id, b.Business_name as CustomerName FROM Business b) AS CP \
            ON c.Customer_id = CP.Customer_id \
            LEFT JOIN Repair r ON c.Customer_id = r.Customer_id \
            LEFT JOIN EmployeeUser eu ON r.Username = eu.Username \
            WHERE c.Customer_id = {Customer_id} \
            ORDER BY r.Start_date DESC, r.VIN DESC, r.Completion_date ASC"

    return query


def get_data_for_template_customerdrill(Customer_id:str,query_type:str):
    # for repairs details
    # print("getting data for: ", query_type)

    if query_type == "sales":
        query = gross_customer_drilldown_sales_query(Customer_id)
    elif query_type == "repair":
        query = gross_customer_drilldown_repair_query(Customer_id)

    data, cols = run_query(query)

    return {'header':cols, 'data':data}


def repair_by_manutypemodel_two_query(manufacturer_name):
    query = f"SELECT Vehicle_type,Model_name,CAST(SUM(Labor_charges) AS numeric(16,2) ) AS All_labor_Costs, \
            CAST(SUM(Total_cost) AS numeric(16,2)) AS Total_Repair_cost, \
            CAST((SUM(Total_cost) - SUM(Labor_charges)) as numeric(16,2)) AS All_Parts_Costs, \
            COUNT(Start_date) AS Count_Repairs \
            from(select 'Car' as VT  \
            UNION select 'SUV' as VT \
            UNION select 'Truck' as VT \
            UNION select 'Convertible' as VT \
            UNION select 'VanMinivan' as VT) as UnionVt \
            JOIN(SELECT v.VIN, VehicleType.Vehicle_type, v.Model_name, r.Labor_charges, r.Total_cost, r.Start_date \
            FROM \
            Vehicle v \
            LEFT JOIN(SELECT Car.VIN, 'Car' AS Vehicle_type FROM Car  \
            UNION SELECT SUV.VIN, 'SUV' AS Vehicle_type FROM SUV \
            UNION SELECT Truck.VIN, 'Truck' AS Vehicle_type FROM Truck \
            UNION SELECT Convertible.VIN, 'Convertible' AS Vehicle_type FROM Convertible \
            UNION SELECT VanMinivan.VIN, 'VanMinivan' AS Vehicle_type FROM VanMinivan \
            ) AS VehicleType ON v.VIN = vehicleType.VIN  \
            JOIN Repair r ON V.VIN = r.VIN \
            WHERE Manufacturer_name = '{manufacturer_name}' \
            ) AS repairs ON repairs.Vehicle_type = UnionVt.VT \
            GROUP BY UnionVt.VT, Vehicle_type, Model_name \
            ORDER BY Vehicle_type,Count_Repairs DESC,Model_name"
    return query

def repair_by_manutypemodel_one_query(manufacturer_name):
    query = f" SELECT VT AS [Vehicle Type],CAST(SUM(Labor_charges) AS numeric (16,2)) AS All_labor_Costs, CAST(SUM(Total_cost) AS numeric (16,2)) AS Total_Repair_cost, \
            CAST((SUM(Total_cost) - SUM(Labor_charges)) as numeric(16,2)) AS All_Parts_Costs,COUNT(Start_date) AS Count_Repairs \
            from (select 'Car' as VT \
                  UNION select 'SUV' as VT \
                  UNION select 'Truck' as VT \
                  UNION select 'Convertible' as VT \
                  UNION select 'VanMinivan' as VT) as UnionVt \
            JOIN (SELECT v.VIN,VehicleType.Vehicle_type,v.Model_name,r.Labor_charges,r.Total_cost,r.Start_date \
            FROM Vehicle v LEFT JOIN (SELECT Car.VIN, 'Car' AS Vehicle_type FROM Car \
            UNION	SELECT SUV.VIN, 'SUV' AS Vehicle_type FROM SUV \
            UNION	SELECT Truck.VIN, 'Truck' AS Vehicle_type FROM Truck \
            UNION	SELECT Convertible.VIN, 'Convertible' AS Vehicle_type FROM Convertible \
            UNION	SELECT VanMinivan.VIN, 'VanMinivan' AS Vehicle_type FROM VanMinivan) AS VehicleType  \
            ON v.VIN= vehicleType.VIN \
            JOIN Repair r ON V.VIN=r.VIN \
            WHERE Manufacturer_name =  '{manufacturer_name}') AS repairs  \
            ON Repairs.Vehicle_type = UnionVt.VT \
            GROUP BY UnionVt.VT \
            ORDER BY Count_Repairs DESC"

    return query


def get_data_for_template_repairby_manutypemodel(manufacturer_name: str,query_type: str):
    if query_type == "one":
        query = repair_by_manutypemodel_one_query(manufacturer_name)
    elif query_type == "two":
        query = repair_by_manutypemodel_two_query(manufacturer_name)
    data, cols = run_query(query)

    return {'header': cols, 'data': data}


def get_detailed_vehicle_query(vin: str):
    user_role = os.environ["USER_ROLE"]

    if user_role not in ["manager", "owner"]:
        query_addition = f" AND v.VIN = '{vin}';"
    else:
        query_addition = f" v.VIN = '{vin}';"

    if user_role in ["manager", "owner"]:
        query = get_query_from_file("vehicle_detailed_manager.txt")

    elif user_role == "inventory_clerk":
        print("getting query for ivc")
        query = get_query_from_file("vehicle_detailed_inventory_clerk.txt")

    elif user_role in ["sales_person", "service_writer"]:
        query = get_query_from_file("vehicle_detailed_worker.txt")

    else:
        query = get_query_from_file("vehicle_detailed_regular.txt")

    return query + query_addition


def get_sales_query(vin: str):
    query_addition = f" WHERE s.VIN IS NOT NULL AND s.VIN = '{vin}';"
    query = get_query_from_file("vehicle_detailed_sales.txt")
    return query + query_addition


def get_repair_query(vin: str):
    query_addition = f" WHERE r.VIN IS NOT NULL AND r.VIN = '{vin}';"
    query = get_query_from_file("vehicle_detailed_repair.txt")
    return query + query_addition


def get_data_for_template(vin: str, query_type: str):
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
        data, cols = cleanup_null_cols(data, cols)
        status = ""
    elif (len(data) == 0) and (query_type == "vehicle"):
        cols = []
        status = "The vehicle is no longer in inventory because it was sold."
    else:
        cols = []
        status = "No results found for: " + query_type

    return {'header': cols, 'data': data, "status": status}
