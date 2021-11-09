import pyodbc
servername = 'LAPTOP-BANS88AD\SQLEXPRESS;'
def run_query(file_name):
    conn = pyodbc.connect('Driver={SQL Server};'
                          f'Server={servername}'
                          'Database=CS6400;'
                          'Trusted_Connection=yes;')
    cursor = conn.cursor()
    with open(file_name, 'r') as file:
        query_string = file.read().replace('\n', ' ')
        print(query_string)
        cursor.execute(query_string)
    results = []
    for i in cursor:
        results.append(i)
    cursor.close()
    return results

results_list1 = run_query('salesByModel')
results_list2 = run_query('salesByType')

print(results_list1)
print(results_list2)

