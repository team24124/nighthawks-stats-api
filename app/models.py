from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column
from sqlalchemy.types import ARRAY, String, Integer, Float
from flask_restful import fields

from app import db
from stats.event import Event
from stats.team import Team

#from stats.team import Team

team_model_fields = {
    'team_number': fields.Integer,
    'team_name': fields.String,
    'country': fields.String,
    'state_province': fields.String,
    'city': fields.String,
    'home_region': fields.String,
    'games_played': fields.Integer,

    'epa_total': fields.Float,
    'auto_epa_total': fields.Float,
    'tele_epa_total': fields.Float,
    'historical_epa': fields.List(fields.Float),
    'historical_auto_epa': fields.List(fields.Float),
    'historical_tele_epa': fields.List(fields.Float),

    'opr': fields.Float,
    'opr_auto': fields.Float,
    'opr_tele': fields.Float,
    'opr_end': fields.Float,
    'historical_opr': fields.List(fields.Float),
    'historical_auto_opr': fields.List(fields.Float),
    'historical_tele_opr': fields.List(fields.Float),
    'historical_end_opr': fields.List(fields.Float)
}

event_model_fields = {
    'event_code': fields.String,
    'event_name': fields.String,
    'country': fields.String,
    'state_province': fields.String,
    'city': fields.String,
    'team_list': fields.List(fields.Integer)
}

class EventModel(db.Model):
    event_code = Column(String, primary_key=True)
    event_name = Column(String)
    country = Column(String)
    state_province = Column(String)
    city = Column(String)
    team_list = Column(ARRAY(Integer))

    def __init__(self, event: Event):
        self.update(event)

    def update(self, event: Event):
        self.event_code = event.event_code
        self.event_name = event.name
        self.country = event.country
        self.state_province = event.state_province
        self.city = event.city
        self.team_list = event.team_list

class TeamModel(db.Model):
    """
    Model used to define the shape of teams in the database with sqlalchemy
    """

    # General Info
    team_number = Column(Integer, primary_key=True)
    team_name = Column(String(80), nullable=False)
    country = Column(String)
    state_province = Column(String)
    city = Column(String)
    home_region = Column(String)
    games_played = Column(Integer)

    # EPA
    epa_total = Column(Float)
    auto_epa_total = Column(Float)
    tele_epa_total = Column(Float)
    historical_epa = Column(ARRAY(Float))
    historical_auto_epa = Column(ARRAY(Float))
    historical_tele_epa = Column(ARRAY(Float))

    # OPR
    opr = Column(Float)
    opr_auto = Column(Float)
    opr_tele = Column(Float)
    opr_end = Column(Float)
    historical_opr = Column(ARRAY(Float))
    historical_auto_opr = Column(ARRAY(Float))
    historical_tele_opr = Column(ARRAY(Float))
    historical_end_opr = Column(ARRAY(Float))

    def __init__(self, team: Team):
        self.update(team)

    def update(self, team: Team):
        self.team_number = team.team_number
        self.team_name = team.name
        self.country = team.country
        self.state_province = team.state_prov
        self.city = team.city
        self.home_region = team.home_region
        self.games_played = team.games_played

        self.epa_total = team.epa_total
        self.auto_epa_total = team.epa_auto_total
        self.tele_epa_total = team.epa_tele_total
        self.historical_epa = team.historical_epa
        self.historical_auto_epa = team.historical_auto_epa
        self.historical_tele_epa = team.historical_tele_epa

        self.opr = team.opr
        self.opr_auto = team.opr_auto
        self.opr_tele = team.opr_tele
        self.opr_end = team.opr_end
        self.historical_opr = team.opr_total_vals
        self.historical_auto_opr = team.opr_auto_vals
        self.historical_tele_opr = team.opr_tele_vals
        self.historical_end_opr = team.opr_end_vals

    def __repr__(self):
        return f"Team(number={self.team_number},name={self.team_name})"