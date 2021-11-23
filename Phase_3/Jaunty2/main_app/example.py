


def run_query(query_string:str):
    """"""
    result = con.run(query_string)
    return result


def read_query(file_path:str):
    with open(file_path, "r") as f:
        query_string = f.read()

    return query_string



user_select_vin = 1234

query = f"SELECT vin, model from Vehicles WHERE vin == {user_select_vin}"

query_from_file = read_query(file_path="get_all_vehicles.txt")

result = run_query(query)

result = read_query(query_from_file)