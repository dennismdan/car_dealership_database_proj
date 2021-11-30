import os
if os.getenv("USER_ROLE") is None:
    os.environ["USER_ROLE"] = "regular_user"

if os.getenv("ADD_USER_TYPE") is None:
    os.environ["ADD_USER_TYPE"] = "individual"


