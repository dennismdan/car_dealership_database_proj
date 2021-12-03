import os
import time
from datetime import datetime, date
from pytz import timezone

import pytest
from ..utils import (gen_query_add_row,
                     run_query,insert_row,
                     get_query_from_file,
                     get_manufacturer_names,
                     compose_pyodbc_connection,
                     cleanup_null_cols,
                     get_detailed_vehicle_query,
                     check_if_instance_exists,
                     is_repair_complete,
                     repair_start_date_is_unique,
                     repair_starts_before_ends,
                     gen_query_update_row,
                     update_row,
                     )

'''
https://coderedirect.com/questions/192135/pyodbc-insert-into-sql
https://thepythonguru.com/inserting-rows/
'''
timezone_est = timezone('EST')

def test_gen_query_update_row():
    table = "Repair"
    update_fields = {"id":5}
    where_fields = {"id":5}
    query = gen_query_update_row(table,update_fields,where_fields)
    print(query)
    assert query == "UPDATE Repair SET id = '5' WHERE id = '5';"
    expected_query = "UPDATE Repair SET Total_cost = '50.00' WHERE VIN = 'VIN02' AND Customer_id = '1' AND Start_date = '2020-12-13';"
    table = "Repair"
    update_fields = {"Total_cost":"50.00"}
    where_fields = {"VIN":'VIN02',"Customer_id":1,"Start_date":'2020-12-13'}
    query = gen_query_update_row(table,update_fields,where_fields)
    print(query)
    assert query == expected_query

def test_update_row():
    val = 190.0
    query = f"UPDATE Repair SET Total_cost = '{val}' WHERE VIN = 'VIN02' AND Customer_id = '1' AND Start_date = '2020-12-13';"
    update_row(query)
    tot_costs = run_query("SELECT Total_cost FROM Repair WHERE VIN = 'VIN02' AND Customer_id = '1' AND Start_date = '2020-12-13';")
    tot_costs = tot_costs[0][0][0]
    print(tot_costs)
    assert tot_costs == val

def test_is_repair_complete():
    data = {"VIN": "00AIVKIDO01487633", "Customer_id": 128, "Start_date": '2020-12-13 00:00:00.000'}
    complete_repair = is_repair_complete(data)

    assert complete_repair

    data = {"VIN": "made-up-vin", "Customer_id": 128, "Start_date": datetime.now(timezone_est).date()}
    complete_repair = is_repair_complete(data)

    assert not complete_repair

    date = datetime.strptime('2020-12-13 00:00:00.000','%Y-%m-%d %H:%M:%S.%f')

    data = {"VIN": "00AIVKIDO01487633", "Customer_id": 128, "Start_date": date}
    complete_repair = is_repair_complete(data)
    assert complete_repair

    date = date.strftime('%Y-%m-%d %H:%M:%S.%f')[0:-3]
    assert '2020-12-13 00:00:00.000' == date

    data = {"VIN": "00AIVKIDO01487633", "Customer_id": 128, "Start_date": date}
    complete_repair = is_repair_complete(data)
    assert complete_repair

def test_repair_start_date_is_unique():
    date = datetime.strptime('2020-12-13 00:00:00.000','%Y-%m-%d %H:%M:%S.%f')

    VIN = "00AIVKIDO01487633"
    Start_date = date

    result = repair_start_date_is_unique(VIN, Start_date)

    assert not result

    result = check_if_instance_exists("Repair",
                                      select_cols = [],
                                      where_clause = [("VIN",VIN),("Start_date",date)])
    assert result

def test_repair_starts_before_ends():
    start_date = datetime.strptime('2020-12-13 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    end_date = datetime.strptime('2020-12-13 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    result = repair_starts_before_ends(start_date,end_date)
    assert result
    start_date = datetime.strptime('2020-12-13 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    end_date = datetime.strptime('2020-12-15 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    result = repair_starts_before_ends(start_date,end_date)
    assert result
    start_date = datetime.strptime('2020-12-13 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    end_date = datetime.strptime('2020-12-10 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    result = repair_starts_before_ends(start_date,end_date)
    assert not result
    start_date = datetime.strptime('2020-12-13 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    end_date = ""
    result = repair_starts_before_ends(start_date,end_date)
    assert result

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

def test_run_query_manual():
    query = "SELECT Total_cost FROM Repair WHERE VIN = '00AIVKIDO01487633' AND Start_date = '2020-12-13'"
    data, cols = run_query(query)
    print("\n Data")
    print(data)
    print(data[0][0])
    assert None is data[0][0]

    query = "SELECT Total_cost FROM Repair WHERE VIN = '00AIVKIDO01487633234' AND Start_date = '2020-12-13'"
    data, cols = run_query(query)
    print("\n Data")

    assert not data


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