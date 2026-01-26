from datetime import datetime

import requests

from stats.averages import get_start_avg
from stats.calculations.epa import update_epa
from stats.calculations.opr import update_opr
from stats.data import get_config, get_auth, get_season_score_parser
from stats.data.api import get_team_from_ftc
from stats.data.scores import EventData
from stats.events import get_all_events
from stats.events.Event import Event
from stats.teams import get_team_data_from_events
from stats.teams.Team import Team
from app.models import PendingEventModel
from stats.events import event_has_teams, get_event_by_code


def calculate_all_stats():
    events = get_all_events()
    return calculate_epa_opr(events)


def calculate_epa_opr(events: list[Event]):
    team_data: dict[int, Team] = {}

    # Get starting avg for EPA calculations
    avg_total, avg_auto, avg_tele = get_start_avg()

    for event in events:
        update_teams_at_event(event, team_data, avg_total, avg_auto, avg_tele)

    return team_data

'''
def update_teams_to_date(last_updated: datetime):
    """
    Finds all new events since last_updated, retries pending events,
    updates team stats, and returns:
      - valid events
      - updated teams
      - still-pending events
    """

    # 1. Fetch ONLY new events
    new_events = get_all_events(
        min_date=last_updated.date(),
        max_date=datetime.today().date()
    )
    print("fetched only new events")

    # 2. Load pending events and resolve them to Event objects
    pending_rows = PendingEventModel.query.all()
    print(pending_rows)
    pending_events = []
    print("looking a pending events")
    for row in pending_rows:
        event = get_event_by_code(row.event_code)
        if event:
            pending_events.append(event)
        print(row)
    print("merging events")
    # 3. Merge + deduplicate by event_code
    all_events = {}
    for event in new_events + pending_events:
        all_events[event.event_code] = event

    valid_events = []
    still_pending = []
    print("validating events")
    # 4. Validate events
    for event in all_events.values():
        if event_has_teams(event.event_code):
            valid_events.append(event)
        else:
            still_pending.append(event)

    # 5. Update team stats USING ONLY valid events
    event_codes = [e.event_code for e in valid_events]

    avg_total, avg_auto, avg_tele = get_start_avg()
    team_data = get_team_data_from_events(event_codes)
    print("Updating teams")
    for event in valid_events:
        update_teams_at_event(event, team_data, avg_total, avg_auto, avg_tele)

    # 6. Return everything (this is the key change)
    return valid_events, team_data, still_pending
'''
def update_teams_to_date(last_updated, pending_event_codes: list[str]):

    # fetch only new events
    new_events = get_all_events(
        min_date=last_updated.date(),
        max_date=datetime.today().date()
    )

    # prepend pending events
    pending_events = [get_event_by_code(code) for code in pending_event_codes]
    all_events = pending_events + new_events

    valid_events = []
    still_pending = []

    for event in all_events:
        if not event:
            continue

        if event_has_teams(event.event_code):
            valid_events.append(event)
        else:
            still_pending.append(event.event_code)

    # 🔥 team calculation happens here
    teams = calculate_teams_from_events(valid_events)

    return valid_events, teams, still_pending






def update_teams_at_event(event: Event, team_data: dict[int, Team], avg_total: float, avg_auto: float, avg_tele: float):
    """
    Update data for all teams using matches from given event code
    :param event: Event object to process
    :param team_data: Team data dictionary with existing statistics/matches. (Key = team_number, Value = team_object)
    :param avg_total: Starting season total average for EPA calculations
    :param avg_auto: Starting season auto average for EPA calculations
    :param avg_tele: Starting season TeleOp average for EPA calculations
    :return: None
    """
    season = get_config()['season']
    event_code = event.event_code
    team_number_list = event.team_list

    game_matrix = create_game_matrix(event_code, team_number_list)
    event_data: EventData = get_season_score_parser(season).parse(event_code)

    for team_number in team_number_list:
        # Process teams that don't exist yet
        if team_number not in team_data.keys():
            team = get_team_from_ftc(team_number)

            # Add starting averages to team data
            team.update_game_played("START")
            team.update_epa(avg_total, avg_auto, avg_tele)

            # Save to team data
            team_data[team_number] = team

    # Skip if the event has no games
    if len(game_matrix) <= 0: return None

    update_opr(team_number_list, game_matrix, event_data, team_data)
    update_epa(team_number_list, game_matrix, event_data, team_data)

    return None


def create_game_matrix(event_code: str, team_list: list[int]):
    """
    Calculates the game matrix, indicating which teams played in which matches
    :param event_code: Valid FIRST Event Code
    :param team_list: Valid list of teams from the event
    :return: The game matrix
    """
    season = get_config()['season']

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

def calculate_teams_from_events(events: list):
    if not events:
        return {}

    event_codes = [e.event_code for e in events]

    avg_total, avg_auto, avg_tele = get_start_avg()
    team_data = get_team_data_from_events(event_codes)

    for event in events:
        update_teams_at_event(event, team_data, avg_total, avg_auto, avg_tele)

    return team_data
