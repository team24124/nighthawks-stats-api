# Create team object to store information
class Team:
    def __init__(self, team_number, name, country, state_prov, city, home_region):
        self.team_number = team_number
        self.name = name

        # Rankings at each event
        self.rankings = {}

        # List of all matches played in consecutive order
        self.matches = []
        self.games_played = len(self.matches)

        self.country = country
        self.state_prov = state_prov
        self.city = city
        self.home_region = home_region

        self.epa_total = 0
        self.epa_auto_total = 0
        self.epa_tele_total = 0
        self.historical_epa = []
        self.historical_auto_epa = []
        self.historical_tele_epa = []
        self.opr_total_vals = []
        self.opr_auto_vals = []
        self.opr_tele_vals = []
        self.opr_end_vals = []
        self.opr = 0
        self.opr_auto = 0
        self.opr_tele = 0
        self.opr_end = 0

    def update_event_rank(self, event_code, event_rank):
        self.rankings[event_code] = event_rank

    def update_game_played(self, match_name):
        self.matches.append(match_name)

    def update_epa(self, new_epa):
        self.epa_total = new_epa
        self.historical_epa.append(new_epa)

    def update_auto_epa(self, new_epa_auto):
      self.epa_auto_total = new_epa_auto
      self.historical_auto_epa.append(new_epa_auto)

    def update_tele_epa(self, new_epa_tele):
      self.epa_tele_total = new_epa_tele
      self.historical_tele_epa.append(new_epa_tele)

    def update_opr(self, opr_total, opr_auto, opr_tele, opr_end):
      self.opr_total_vals.append(float(opr_total)) # Connvert numpy floats to python floats
      self.opr_auto_vals.append(float(opr_auto))
      self.opr_tele_vals.append(float(opr_tele))
      self.opr_end_vals.append(float(opr_end))
      self.opr = float(opr_total)
      self.opr_auto = float(opr_auto)
      self.opr_tele = float(opr_tele)
      self.opr_end = float(opr_end)

    def __repr__(self):
        return f"Team #{self.team_number} | Games Played: {self.games_played} | EPA Total: {self.epa_total}"