from datetime import datetime
import requests

import stats.event as event
import stats.opr_epa as opr_epa
import stats.team as team
import stats.data as data
from stats.config import config
from stats.opr_epa import update_epa_opr_to_today

if __name__ == '__main__':
    #print(requests.get(f"https://nighthawks-stats-eight.vercel.app/api/teams/24124/").status_code != 404)
    teams = update_epa_opr_to_today(datetime.fromisoformat("2025-06-28"))
    for team in teams.values():
        print(team.matches)