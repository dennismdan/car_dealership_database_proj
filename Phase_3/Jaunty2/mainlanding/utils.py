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
    query = "SELECT * FROM Vehicle WHERE "
    where_clause = ["col1=value1", "", ""]
    for key, val in user_input.items():
        where_clause.append(f"{key}={val}")

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
    return colors

def get_query_from_file(file_name:str)->str:
    cwd = os.getcwd()
    sql_path = os.path.join(cwd,"mainlanding\SQL")
    file_path = os.path.join(sql_path,file_name)

    with open(file_path, 'r') as file:
        query_string = file.read().replace('\n', ' ').replace('\t','')
        query_string = query_string.replace("  "," ").replace("   "," ")
    return query_string


print(get_query_from_file("search_veh_by_vin.txt"))