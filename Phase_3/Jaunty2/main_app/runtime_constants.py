import os

SERVER = os.getenv("DB_SERVER", "MAORYZEN7\SQLEXPRESS")

USER_ROLE = os.getenv("USER_ROLE", "regular_user")

WORKERS = ["owner","manager","inventory_clerk","sales_person","service_writer"]

class EnvError(Exception):
    pass


if SERVER is None:
    raise EnvError("Environment variable for server was not set.\
     Add server env variable so you can run the code with a database.")
