from .runtime_constants import SERVER

'''
TODO:
1. Update the generate_query function to handle SELCET, DELETE, UPDATE, INSERT
2. Create a folder with all report or long queries in text files
3. Create a function that reads the queries from text files and returns string

'''

from typing import Tuple, List
import pyodbc


def generate_query(user_input: dict) -> str:
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


def run_query(query: str) -> List[tuple]:
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
    results = []
    for i in cursor:
        results.append(i)
    header = [column[0] for column in cursor.description]
    cursor.close()
    return results, header


def get_colors():
    query = "SELECT DISTINCT Color FROM Color"
    colors, cols = run_query(query)
    colors = [(i, colors[i][0]) for i in range(len(colors))]
    return colors
