from .runtime_constants import SERVER

import os

'''
TODO:
1. Update the generate_query function to handle SELCET, DELETE, UPDATE, INSERT
2. Create a folder with all report or long queries in text files
3. Create a function that reads the queries from text files and returns string

'''

from typing import Tuple, List
import pyodbc

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

    return query

def run_query(query:str,return_results:bool = True)->List[tuple]:
    '''
    :param query:
    :return:
    '''

    conn = pyodbc.connect('Driver={SQL Server};'
                          f'Server={SERVER};'
                          'Database=CS6400;'
                          'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute(query)

    results = None
    header = None
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

    conn = pyodbc.connect('Driver={SQL Server};'
                          f'Server={SERVER};'
                          'Database=CS6400;'
                          'Trusted_Connection=yes;')
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
    sql_path = os.path.join(cwd,"mainlanding\SQL")
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