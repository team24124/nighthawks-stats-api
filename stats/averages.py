from datetime import datetime

from stats.config import config
from stats.score_data import obtain_score_data


def calculate_start_avg(events):
    """
    Calculates the start of the season average for use in EPA calculations
    :param events: List of (event date, event code) objects to consider
    :return: Average total score, average auto score, average teleop score
    """
    season = config['season']
    first_events = []

    for event in events:
        iso_date = event[0]
        event_code = event[1]['code']

        date = datetime.fromisoformat(iso_date)
        if date.month == 11 or date.month == 10:  # Find events in October (10) or November (11)
            print(f"Found early event (${event_code})")
            first_events.append(event_code)

    num_games = avg_total = avg_auto = avg_teleop = 0
    # Find the averages in the first number of events
    for event in first_events:
        print(f"Parsing event scores from early event")
        event_total_scores, event_auto_scores, event_tele_scores, event_end_scorse = obtain_score_data(season, event)
        num_games += len(event_total_scores)
        avg_total += sum(event_total_scores)
        avg_auto += sum(event_auto_scores)
        avg_teleop += sum(event_tele_scores)

    avg_total /= num_games
    avg_total /= 2

    avg_auto /= num_games
    avg_auto /= 2

    avg_teleop /= num_games
    avg_teleop /= 2

    print(f"Average Total: {avg_total}, Average Auto: {avg_auto}, Average TeleOP: {avg_teleop}")
    return avg_total, avg_auto, avg_teleop