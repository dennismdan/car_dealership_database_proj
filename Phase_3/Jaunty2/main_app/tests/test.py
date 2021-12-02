import os
import time

import pytest
from ..utils import (gen_query_add_row,
                     run_query,insert_row,
                     get_query_from_file,
                     get_manufacturer_names,
                     compose_pyodbc_connection,
                     cleanup_null_cols,
                     get_detailed_vehicle_query,
                     check_if_instance_exists)

'''
https://coderedirect.com/questions/192135/pyodbc-insert-into-sql
https://thepythonguru.com/inserting-rows/
'''

def test_check_if_instance_exists():
    result = check_if_instance_exists("test_table_02",["Phone_number"],[("id",1)])
    assert not result
    result = check_if_instance_exists("Car",["VIN"],[("VIN",'073HOEWCHAF741925')])
    assert result
    result = check_if_instance_exists("Car",["VIN"],[("VIN",'073HOEWCHAF741925'),("Doors_count",5)])
    assert not result

def test_gen_query_add_row():
    table = 'test_table'
    row = ("val",)
    query = gen_query_add_row(table,row)
    expected = "INSERT INTO test_table(col1) VALUES (?) "
    assert query == expected
    table = 'test_table_02'
    row = ("Phone_number","Email")
    query = gen_query_add_row(table,row, skip_col_list=["id"])
    expected = "INSERT INTO test_table_02(Phone_number,Email) VALUES (?,?) "
    assert query == expected


def test_run_query():
    data, cols = run_query("SELECT * FROM test_table")
    assert len(data) > 0 and len(cols) > 0

def test_insert_row():
    table = 'test_table'
    dataBefore,_ = run_query(f"SELECT * FROM {table};")
    index = len(dataBefore)
    row = (f"val_{index}",)
    query = gen_query_add_row(table,row)

    insert_row(query,row)
    time.sleep(2)
    dataAfter, _ = run_query(f"SELECT * FROM {table};")

    assert len(dataBefore)+1 == len(dataAfter)


def test_get_query_from_file():
    expected = """SELECT * FROM test_table GROUP BY col1 HAVING COUNT(*) > 2 ORDER BY col1"""
    query = get_query_from_file("test_query")
    dataBefore,_ = run_query(expected)
    index = len(dataBefore)
    assert index > 0
    assert expected == query

def test_get_manufacturer_names():
    data = get_manufacturer_names()
    assert len(data)>0

def test_get_search_vehicle_query():
    data = get_query_from_file("query_vehicle.txt")
    print(data)
    assert True

def test_compose_pyodbc_connection():
    connect_str = compose_pyodbc_connection()
    print(connect_str)
    os.environ["PYODBC_AUTH"] = "True"
    os.environ["PYODBC_USER"] = "Dennis"
    os.environ["PYODBC_PW"] = "####"
    connect_str = compose_pyodbc_connection()
    print(connect_str)
    os.environ["PYODBC_AUTH"] = "False"
    assert True


def test_cleanup_null_cols():
    test_data = [(1,None,"a",None),(1,None,"a","b")]
    test_cols = ["a","b","c","d"]
    data,cols = cleanup_null_cols(test_data,test_cols)

    assert data == [(1,"a",None),(1,"a","b")]
    assert cols == ["a","c","d"]

def test_get_detailed_vehicle_query():
    os.environ["USER_ROLE"] = "inventory_clerk"
    print(os.environ["USER_ROLE"])
    query = get_detailed_vehicle_query("0")
    print(query)
    d,h = run_query(query)
    print(d,h)


    os.environ["USER_ROLE"] = "manager"
    print(os.environ["USER_ROLE"])
    query = get_detailed_vehicle_query("0")
    print(query)
    d,h = run_query(query)
    print(d,h)

    os.environ["USER_ROLE"] = "regular_user"
    print(os.environ["USER_ROLE"])
    query = get_detailed_vehicle_query("0")
    print(query)
    d,h = run_query(query)
    print(d,h)

    assert True