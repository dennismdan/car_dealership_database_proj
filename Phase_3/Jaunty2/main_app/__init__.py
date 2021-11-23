import os
if os.getenv("USER_ROLE") is None:
    os.environ["USER_ROLE"] = "regular_user"

