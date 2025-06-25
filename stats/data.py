import os
from dotenv import load_dotenv


def get_auth():
    """
    Get the authentication header required for FIRST API calls from environment variables

    :return
        A tuple contained the username and tokenn
    """
    load_dotenv()
    return os.getenv("API_USER"), os.getenv("API_TOKEN")
