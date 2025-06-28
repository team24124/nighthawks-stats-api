import requests

from stats.data import get_auth


def obtain_score_data(season: int, event_code: str):
    """
    Obtain score data broken into components for a given event and season.
    :param season: A valid integer representing the season year
    :param event_code: A valid FIRST event code to draw events from
    :return:A tuple of the match name, and each score component: total score, auto score, teleop score and endgame score
    """
    # Pulling a request for the scores with different parameters
    response = requests.get(f"https://ftc-api.firstinspires.org/v2.0/{season}/scores/" + event_code + "/qual",
                            auth=get_auth())  # only grab from qualifiers to equally compare all teams
    score_data = response.json()['matchScores']

    match season:
        case 2024:
            return obtain_2024_score_data(score_data, event_code)
    raise Exception(f"A valid season was not found. We could not find the function to calculate component scores for the {season} season.")


def obtain_2024_score_data(score_data, event_code):
    """
    Calculates a list of the scores, broken into components for the 2024 season (Into the Deep)

    :param event_code: Valid FIRST event code
    :param score_data: JSON response for all match scores at an event
    :return: A tuple of the match name and each score component: total score, auto score, teleop score and endgame score
    """
    match_names = []
    auto_score = []
    teleop_score = []
    endgame_score = []
    total_score = []

    for match_score in score_data:
        # Match name in the format: [season][event][qualification][match_number]
        match_level = 'q' if match_score['matchLevel'] == "QUALIFICATION" else "p"
        match_name = f"2024{event_code}{match_level}{match_score['matchNumber']}"
        match_names.append(match_name)

        red_alliance = match_score['alliances'][1]
        blue_alliance = match_score['alliances'][0]

        # Add red alliance
        total_score.append(red_alliance['preFoulTotal'])
        auto_score.append(red_alliance['autoPoints'])
        teleop_sample_spec = red_alliance['teleopSamplePoints'] + red_alliance[
            'teleopSpecimenPoints']
        teleop_score.append(teleop_sample_spec)

        endgame_score.append(red_alliance['teleopPoints'] - teleop_sample_spec)

        # Then blue alliance
        total_score.append(blue_alliance['preFoulTotal'])
        auto_score.append(blue_alliance['autoPoints'])
        teleop_sample_spec = blue_alliance['teleopSamplePoints'] + blue_alliance[
            'teleopSpecimenPoints']
        teleop_score.append(teleop_sample_spec)

        endgame_score.append(blue_alliance['teleopPoints'] - teleop_sample_spec)

    return match_names, total_score, auto_score, teleop_score, endgame_score