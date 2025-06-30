from datetime import datetime
from typing import Dict

import requests
from stats.data import get_auth
from stats.event import create_team_list, get_all_events, get_all_events_by_teams
from stats.score_data import obtain_score_data
from stats.team import Team
from stats.config import config
import numpy as np


def create_game_matrix(event_code, team_list):
    """
    Calculates the game matrix, indicating which teams played in which matches
    :param event_code: Valid FIRST Event Code
    :param team_list: Valid list of teams from the event
    :return: The game matrix
    """
    season = config['season']

    response = requests.get(
        f"http://ftc-api.firstinspires.org/v2.0/{season}/matches/" + event_code + "?tournamentLevel=qual", auth=get_auth())
    matches = response.json()['matches']  # only grab from qualifiers to equally compare all teams

    game_matrix = []

    # Add 1 to row at index where team number is in list
    for match in matches:
        red_alliances = [0] * len(team_list)
        blue_allainces = [0] * len(team_list)

        # for each match find if each team is on a red or blue alliance team
        for team in match['teams']:
            alliance = team['station']
            if alliance == 'Red1' or alliance == 'Red2':
                red_alliances[team_list.index(team['teamNumber'])] = 1
            else:
                blue_allainces[team_list.index(team['teamNumber'])] = 1

        game_matrix.append(red_alliances)
        game_matrix.append(blue_allainces)

    return game_matrix


def calculate_event_epa_opr(event_code, region_code=""):
    """
    Calculate and update epa and opr for all teams at a specified event
    :param event_code: Valid FIRST event code
    :param region_code: Optional, region code used to determine starting averages for EPA
    :return: A list of all teams who have participated in an event with updated statistics
    """
    teams = create_team_list(event_code)
    events = get_all_events_by_teams(teams) # Get all events that the teams have participated in


    all_teams = calculate_epa_opr(events, region_code) # Calculate relevant epa/opr for all teams in those events

    print("Filtering for teams in the event")
    event_teams = {str(team): all_teams[team] for team in teams} # Filter for teams at the specified event

    print("Calculations complete!")
    return event_teams

def calculate_world_epa_opr(region_code=""):
    all_teams: dict[str, Team]
    all_events = get_all_events()
    all_teams = calculate_epa_opr(all_events, region_code)

    print("Calculations complete!")
    return all_teams


def calculate_epa_opr(events, region_code=""):
    """
    Calculate and update epa and opr for all teams, able to be filtered by specifying a list of events
    :param events: List of (event start date, event code) object
    :param region_code: (OPTIONAL) Region Code to use while determining starting average
    :return: A list of all teams who have participated in atleast one of the given events with updated statistics
    """
    season = config['season']
    all_teams: dict[str, Team] = {}

    # Calculate Averages
    if config['calculate_averages']:
        if region_code:
            print("Calculating Starting Averages from Region:", region_code)
        else:
            print("Calculating Starting Average from World Teams")
        early_events = get_all_events() if region_code == "" else get_all_events(region_code)

        from stats.averages import calculate_start_avg
        avg_total, avg_auto, avg_teleop = calculate_start_avg(early_events)
    else:
        avg_total = config['averages']['overall']
        avg_auto = config['averages']['auto']
        avg_teleop = config['averages']['teleop']
        print(f"Using predetermined averages ({avg_total}, {avg_auto}, {avg_teleop})")

    event_codes = [event[1]['code'] for event in events] # get event codes from tuple

    for event in event_codes:
        process_event(event, avg_total, avg_auto, avg_teleop, all_teams)

    return all_teams


def get_epa_parameters(team_red_1: Team, team_red_2: Team, team_blue_1: Team, team_blue_2: Team):
    """
    Calculate the correct m and k EPA parameters given 4 teams
    :param team_red_1: A valid team object
    :param team_red_2: A valid team object
    :param team_blue_1: A valid team object
    :param team_blue_2: A valid team object
    :return: m and k values for EPA calculation
    """
    k = 0.33
    m = 0
    games_played = (team_red_1.games_played + team_red_2.games_played +
                    team_blue_1.games_played + team_blue_2.games_played) / 4
    if 6 < games_played <= 12:
        k = 0.33 - (games_played - 6) / 45
    elif 12 < games_played <= 36:
        k = 0.2
        # m = (games_played - 12)/24 # Commented out due to non-defensive nature of this season's game
    elif games_played > 36:
        k = 0.2
        # m = 1

    return m, k


# Team Specific Functions
def update_epa(team_red_1: Team, team_red_2: Team, team_blue_1: Team, team_blue_2: Team, red_score: int,
               blue_score: int):
    """
    Update epa for all provided teams given a score for both
    :param team_red_1: A valid team object
    :param team_red_2: A valid team object
    :param team_blue_1: A valid team object
    :param team_blue_2: A valid team object
    :param red_score: Nonpenalty total score for the red alliance
    :param blue_score: Nonpenalty total score for the blue alliance
    """

    m, k = get_epa_parameters(team_red_1, team_red_2, team_blue_1, team_blue_2)

    red_epa = team_red_1.epa_total + team_red_2.epa_total
    blue_epa = team_blue_1.epa_total + team_blue_2.epa_total

    delta_epa_red = k / (1 + m) * ((red_score - red_epa) - m * (blue_score - blue_epa))
    delta_epa_blue = k / (1 + m) * ((blue_score - blue_epa) - m * (red_score - red_epa))

    team_red_1.update_epa(team_red_1.epa_total + delta_epa_red)
    team_red_2.update_epa(team_red_2.epa_total + delta_epa_red)
    team_blue_1.update_epa(team_blue_1.epa_total + delta_epa_blue)
    team_blue_2.update_epa(team_blue_2.epa_total + delta_epa_blue)


def update_epa_auto(team_red_1: Team, team_red_2: Team, team_blue_1: Team, team_blue_2: Team, red_score: int,
                    blue_score: int):
    """
    Update epa for all provided teams given a score for both
    :param team_red_1: A valid team object
    :param team_red_2: A valid team object
    :param team_blue_1: A valid team object
    :param team_blue_2: A valid team object
    :param red_score: Total auto score for the red alliance
    :param blue_score: Total auto score for the blue alliance
    """

    m, k = get_epa_parameters(team_red_1, team_red_2, team_blue_1, team_blue_2)

    red_epa = team_red_1.epa_auto_total + team_red_2.epa_auto_total
    blue_epa = team_blue_1.epa_auto_total + team_blue_2.epa_auto_total

    delta_epa_red = k / (1 + m) * ((red_score - red_epa) - m * (blue_score - blue_epa))
    delta_epa_blue = k / (1 + m) * ((blue_score - blue_epa) - m * (red_score - red_epa))

    team_red_1.update_auto_epa(team_red_1.epa_auto_total + delta_epa_red)
    team_red_2.update_auto_epa(team_red_2.epa_auto_total + delta_epa_red)
    team_blue_1.update_auto_epa(team_blue_1.epa_auto_total + delta_epa_blue)
    team_blue_2.update_auto_epa(team_blue_2.epa_auto_total + delta_epa_blue)


def update_epa_tele(team_red_1: Team, team_red_2: Team, team_blue_1: Team, team_blue_2: Team, red_score: int,
                    blue_score: int):
    """
    Update epa for all provided teams given a score for both
    :param team_red_1: A valid team object
    :param team_red_2: A valid team object
    :param team_blue_1: A valid team object
    :param team_blue_2: A valid team object
    :param red_score: Total teleop score for the red alliance
    :param blue_score: Total teleop score for the blue alliance
    """

    m, k = get_epa_parameters(team_red_1, team_red_2, team_blue_1, team_blue_2  )

    red_epa = team_red_1.epa_tele_total + team_red_2.epa_tele_total
    blue_epa = team_blue_1.epa_tele_total + team_blue_2.epa_tele_total

    delta_epa_red = k / (1 + m) * ((red_score - red_epa) - m * (blue_score - blue_epa))
    delta_epa_blue = k / (1 + m) * ((blue_score - blue_epa) - m * (red_score - red_epa))

    team_red_1.update_tele_epa(team_red_1.epa_tele_total + delta_epa_red)
    team_red_2.update_tele_epa(team_red_2.epa_tele_total + delta_epa_red)
    team_blue_1.update_tele_epa(team_blue_1.epa_tele_total + delta_epa_blue)
    team_blue_2.update_tele_epa(team_blue_2.epa_tele_total + delta_epa_blue)

def process_event(event_code: str, avg_total: float, avg_auto: float, avg_teleop:float, all_teams: Dict[str, Team]):
    season = config['season']
    team_list = create_team_list(event_code)  # List of team numbers needed
    team_number_list = []
    print(f"Processing {len(team_list.values())} teams from event: {event_code}")
    for team_number in team_list:
        team = team_list[team_number]
        team_number_list.append(team.team_number)
        team.update_game_played("START")
        team.update_epa(avg_total)
        team.update_auto_epa(avg_auto)
        team.update_tele_epa(avg_teleop)

        # Add the newly created team if they don't already exxist
        if team_number not in all_teams.keys():
            all_teams[team.team_number] = team

        # If this event is in the newly created teams rankings, update their ranking in our representation
        if event_code in team.rankings:
            all_teams[team.team_number].update_event_rank(event_code, team.rankings[event_code])
    game_matrix = create_game_matrix(event_code, team_number_list)

    if len(game_matrix) > 0:  # skip events with no games
        # Get relevant scoring data from the event
        match_names, total_match_score, auto_match_score, tele_match_score, end_match_score = obtain_score_data(season,
                                                                                                                event_code)

        # Calculate OPR
        total_opr = np.linalg.lstsq(game_matrix, total_match_score)[0]
        auto_opr = np.linalg.lstsq(game_matrix, auto_match_score)[0]
        tele_opr = np.linalg.lstsq(game_matrix, tele_match_score)[0]
        end_opr = np.linalg.lstsq(game_matrix, end_match_score)[0]

        for i in range(len(team_number_list)):
            team_number = team_number_list[i]  # Use team number from team list to get team
            team_obj = all_teams[team_number]
            team_obj.update_opr(total_opr[i], auto_opr[i], tele_opr[i], end_opr[i])

        # Calculate EPA
        game_index = 0
        for i in range(0, len(game_matrix), 2):
            red_index = np.where(np.array(game_matrix[i]) == 1)[0]
            team1 = all_teams[team_number_list[red_index[0]]]
            team2 = all_teams[team_number_list[red_index[1]]]

            blue_index = np.where(np.array(game_matrix[i + 1]) == 1)[0]
            team3 = all_teams[team_number_list[blue_index[0]]]
            team4 = all_teams[team_number_list[blue_index[1]]]

            if match_names[game_index] in team1.matches: # Check if this match has already been processed as a precaution
                game_index += 1
                continue

            # Use i as the index the red alliances score, therefore i+1 will be the index of the blue alliances'
            team1.update_game_played(match_names[game_index])
            team2.update_game_played(match_names[game_index])
            team3.update_game_played(match_names[game_index])
            team4.update_game_played(match_names[game_index])
            update_epa(team1, team2, team3, team4, total_match_score[i], total_match_score[i + 1])
            update_epa_auto(team1, team2, team3, team4, auto_match_score[i], auto_match_score[i + 1])
            update_epa_tele(team1, team2, team3, team4, tele_match_score[i], tele_match_score[i + 1])

            game_index += 1


def update_epa_opr_to_today(last_updated: datetime):
    """
    Finds and calculates statistics for all events between a given datetime and the time the function is called.
    Uses preexisting statistics found via API call.
    :param last_updated: Lowerbound datetime to find events
    :return: Tuple of the list of processed events, and team statistics
    """
    today = datetime.now()
    events = get_all_events()
    new_events = []
    teams = {}

    for event in events:
        iso_date = event[1]['dateEnd']
        event_code = event[1]['code']

        date = datetime.fromisoformat(iso_date).date()

        if last_updated.date() <= date < today.date():
            new_events.append(event[1])
            for team_number, team_obj in create_team_list(event_code).items():
                res = requests.get(f"https://nighthawks-stats.vercel.app/api/teams/{team_number}/")
                if res.status_code != 404:
                    team_data = res.json()
                    team_obj.update(team_data)
                teams[team_number] = team_obj

    print(new_events)
    # Calculate Averages
    if config['calculate_averages']:
        early_events = get_all_events()

        from stats.averages import calculate_start_avg
        avg_total, avg_auto, avg_teleop = calculate_start_avg(early_events)
    else:
        avg_total = config['averages']['overall']
        avg_auto = config['averages']['auto']
        avg_teleop = config['averages']['teleop']

    # Process events
    for event in new_events:
        event_code = event['code']
        process_event(event_code, avg_total, avg_auto, avg_teleop, teams)

    return new_events, teams
    # Loop through each event and call process_event
    # Return the newly updated teams list to be comitted
    #TODO: ADD END DATE TO EVENT