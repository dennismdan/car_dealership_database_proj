# 1. generate query from user input
# 2. Run query
#...

from typing import Tuple,List
import pyodbc
servername = 'LAPTOP-BANS88AD\SQLEXPRESS;'


def generate_query(user_input:dict)->str:
    '''
    :param user_input: dictionary of form {col1:value,col2:value}
    :return:

    TODO: format query per project structure
    
    '''
    query = "SELECT * FROM Vehicle WHERE "
    where_clause = ["col1=value1","",""]
    for key,val in user_input.items():
        where_clause.append(f"{key}={val}")

    query += " AND ".join(where_clause)
    return query


def run_query(query:str)->List[tuple]:
    '''
    TODO:
    1. make a connection to database
    2. Update servername
    2. run query on database
    3. return results


    :param query:
    :return:
    '''
    print(query)
    # conn = pyodbc.connect('Driver={SQL Server};'
    #                       f'Server={servername}'
    #                       'Database=CS6400;'
    #                       'Trusted_Connection=yes;')
    # cursor = conn.cursor()
    #
    # cursor.execute(query)
    # results = []
    # for i in cursor:
    #     results.append(i)
    #header = [column[0] for column in cursor.description]
    # cursor.close()
    header = ["Vehicle_type","Manufacturer_name","Year","Color","Price"]
    results = [("SUV","toyota",2010,"red",2100),
               ("Sedan","Tesla",2020,"red",5400),
               ("Sedan","TeslaMod3",2010,"red",2100),
               ("Truck","CyberTruck",2010,"red",2100)]
    return results, header

