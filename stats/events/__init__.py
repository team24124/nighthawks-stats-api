from datetime import date, datetime

import requests

from stats.data import get_config, get_auth
from stats.events.Event import Event


def create_team_list(event_code: str) -> list[int]:
  """
  Generate a list of team numbers from an event given an event code
  :param event_code: FIRST Event Code
  :return: List of all team's numbers from the event
  """
  season = get_config()['season']

  team_response = requests.get(f"https://ftc-api.firstinspires.org/v2.0/{season}/teams?eventCode="+event_code, auth=get_auth())
  teams_at_comp = team_response.json()['teams']

  teams = [team['teamNumber'] for team in teams_at_comp]

  return teams


def get_event(event_code: str) -> Event:
  """
  Get an event object from a given event code
  :param event_code: Valid FTC Event Code
  :return: Event object
  """
  season = get_config()['season']
  event_response = requests.get(f"http://ftc-api.firstinspires.org/v2.0/{season}/events?eventCode={event_code}",
                                auth=get_auth())

  if event_response.status_code == 404:
    raise ValueError(f"The event {event_code} you tried to find does not exist.")

  event_data = event_response.json()['events'][0]

  return Event(event_data)


def get_division_events(event_code: str) -> list[Event]:
  """
  Get all associated divisions for an event given an event code.
  :param event_code: Event code to find division events from
  :return: List of division events, empty if none
  """
  season = get_config()['season']
  division_events: list[Event] = []

  event_response = requests.get(f"http://ftc-api.firstinspires.org/v2.0/{season}/events", auth=get_auth())
  all_event_data = event_response.json()['events']

  division_event_codes = [event['code'] for event in all_event_data if event['divisionCode'] == event_code]
  for event_code in division_event_codes:
    division_events.append(get_event(event_code))

  return division_events


def get_all_events(region: str = "", min_date: date = date.min, max_date: date = date.max) -> list[Event]:
  """
  Get all events within parameters. By default, returns all events.
  :param region: OPTIONAL, get events from a certain region with given region code
  :param min_date: OPTIONAL, get events that end after a certain date
  :param max_date: OPTIONAL, get events that end before a certain date
  :return: List of all events that fit the given criteria
  """
  from stats.events.Event import Event
  config = get_config()

  valid_events = config['allowed_events']
  season = config['season']

  event_response = requests.get(f"http://ftc-api.firstinspires.org/v2.0/{season}/events", auth=get_auth())
  all_event_data = event_response.json().get('events', [])

  events: list[Event] = []

  for event_data in all_event_data:
    # If we specify a region, and the event is not in that region skip it
    if region and region != event_data['regionCode']: continue

    # If the event does not fall between the min/max dates skip it
    end_date = datetime.fromisoformat(event_data['dateEnd']).date()
    if end_date < min_date or end_date > max_date: continue

    # If the event is not an allowed event type skip it
    event_type = int(event_data['type'])
    if event_type not in valid_events: continue


    events.append(Event(event_data))

  # Sort by ascending start date
  events.sort(key=lambda event: datetime.fromisoformat(event.dateStart).date())

  return events


def get_event_rankings(event_code: str) -> dict[int, int]:
  """
  Get event rankings for each team from a given event code
  :param event_code: Valid FTC Event Code
  :return: Dictionary where the key is a team number and the value is the team's rank at the evvent, empty if no ranking
  """
  season = get_config()['season']
  rank_response = requests.get(f"http://ftc-api.firstinspires.org/v2.0/{season}/rankings/{event_code}", auth=get_auth())

  if rank_response.status_code == 404:
    raise ValueError(f"The event {event_code} you tried to find does not exist.")

  rank_data = rank_response.json()['rankings']
  rankings = {rank['teamNumber']: rank['rank'] for rank in rank_data}

  return rankings
