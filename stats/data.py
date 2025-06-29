import os
from dotenv import load_dotenv
from datetime import datetime


def get_auth():
    """
    Get the authentication header required for FIRST API calls from environment variables

    :return
        A tuple containing the username and token
    """
    load_dotenv()
    return os.getenv("API_USER"), os.getenv("API_TOKEN")

def parse_date(date: str):
    """
    Parse a datetime object using the postgres date format
    :return: datetime object
    """
    return datetime.strptime(date, '%a, %d %b %Y %H:%M:%S -0000')
