import datetime

import requests

import stats.event as event
import stats.opr_epa as opr_epa
import stats.team as team
import stats.data as data
from stats.config import config

if __name__ == '__main__':
    x = opr_epa.calculate_event_epa_opr("CAABCMP", "CAAB")
    for team in x.values():
        print(f"{team.team_number} {team.games_played}")