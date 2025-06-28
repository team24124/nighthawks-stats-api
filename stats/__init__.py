import stats.event as event
import stats.opr_epa as opr_epa
import stats.team as team
import stats.data as data
from stats.opr_epa import calculate_event_epa_opr, calculate_world_epa_opr

if __name__ == '__main__':

    teams = calculate_event_epa_opr("CAABCMP")
    for team, data in teams.items():
        print(team)
        print(data.matches)
