
import requests
from stats.data import get_config
from stats.data.scores import AllianceScoreData, MatchData, EventData

class DecodeScoreParser:
    def parse(self, event_code: str) -> EventData:
        from stats.data import get_auth
        season = get_config()['season']
        r = requests.get(
            f"https://ftc-api.firstinspires.org/v2.0/2025/scores/" + event_code + "/qual",
                                auth=get_auth()
        )
        print(r.status_code)
        print(r.text)
        data = r.json()

        event_data = EventData()

        for match in data['matchScores']:
            match_number = match['matchNumber']
            match_level = match['matchLevel'][0].upper()  # Q for qualification, P for playoffs

            alliances = match['alliances']

            # Find Red and Blue alliance data
            red_data = next(a for a in alliances if a['alliance'].lower() == 'red')
            blue_data = next(a for a in alliances if a['alliance'].lower() == 'blue')

            # Build AllianceScoreData objects
            red_scores = AllianceScoreData(
                total_score=red_data.get('totalPoints', 0) - blue_data.get('foulPointsCommitted', 0),
                auto_score=(red_data.get('autoArtifactPoints', 0) +red_data.get('autoLeavePoints', 0) + red_data.get('autoPatternPoints', 0)),
                tele_score=(
                        red_data.get('teleopArtifactPoints', 0) +
                        red_data.get('teleopDepotPoints', 0) +
                        red_data.get('teleopPatternPoints', 0)

                ),
                end_score=red_data.get('teleopBasePoints', 0)  # If there’s a separate endgame score, set it; otherwise 0
            )

            blue_scores = AllianceScoreData(
                total_score=blue_data.get('totalPoints', 0) - red_data.get('foulPointsCommitted', 0),
                auto_score=(blue_data.get('autoArtifactPoints', 0) + blue_data.get('autoLeavePoints', 0) + blue_data.get(
                    'autoPatternPoints', 0)),
                tele_score=(
                        blue_data.get('teleopArtifactPoints', 0) +
                        blue_data.get('teleopDepotPoints', 0) +
                        blue_data.get('teleopPatternPoints', 0)

                ),
                end_score=blue_data.get('teleopBasePoints', 0)
            )

            match_obj = MatchData(
                season=season,
                event_code=event_code,
                match_number=match_number,
                match_level=match_level,
                red_scores=red_scores,
                blue_scores=blue_scores
            )

            event_data.add(match_obj)

        return event_data