import time

import pytest
from ..utils import gen_query_add_row, run_query,insert_row
'''
https://coderedirect.com/questions/192135/pyodbc-insert-into-sql
https://thepythonguru.com/inserting-rows/
'''



def test_gen_query_add_row():
    table = 'test_table'
    row = ("val",)
    query = gen_query_add_row(table,row)
    expected = "INSERT INTO test_table(col1) VALUES (?) "
    assert expected == query


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


