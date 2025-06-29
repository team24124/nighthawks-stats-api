import datetime

import requests

import stats.event as event
import stats.opr_epa as opr_epa
import stats.team as team
import stats.data as data
from stats.config import config

if __name__ == '__main__':
    dt = requests.get("http://127.0.0.1:5000/api/info/").json()
    print(dt['last_updated'])
    print(datetime.datetime.strptime(dt['last_updated'], '%a, %d %b %Y %H:%M:%S -0000').date())