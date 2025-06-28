import os
from dotenv import load_dotenv


def get_auth():
    """
    Get the authentication header required for FIRST API calls from environment variables

    :return
        A tuple containing the username and token
    """
    load_dotenv()
    return os.getenv("API_USER"), os.getenv("API_TOKEN")
