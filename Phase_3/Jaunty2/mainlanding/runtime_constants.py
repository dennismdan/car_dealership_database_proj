import os

SERVER = os.getenv("DB_SERVER", "MAORYZEN7\SQLEXPRESS")


class EnvError(Exception):
    pass


if SERVER is None:
    raise EnvError("Environment variable for server was not set.\
     Add server env variable so you can run the code with a database.")
