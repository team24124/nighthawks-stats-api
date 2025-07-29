import datetime

from flask import render_template
from flask_restful import Resource, marshal_with, abort
from app.models import TeamModel, team_model_fields, event_model_fields, EventModel, AppMetaData, meta_data_fields

from app import app, api, db
from stats.data import parse_date
from stats.events import get_all_events, Event as EventObj
from stats.calculations import calculate_all_stats, update_teams_to_date

class MetaData(Resource):
    @marshal_with(meta_data_fields)
    def get(self):
        return AppMetaData.query.get(0)

    # @marshal_with(meta_data_fields)
    # def post(self):
    #     metadata = AppMetaData(last_updated=datetime.datetime.now())
    #     db.session.add(metadata)
    #     db.session.commit()
    #     return metadata

class Teams(Resource):
    @marshal_with(team_model_fields)
    def get(self):
        return TeamModel.query.all()

class Team(Resource):
    @marshal_with(team_model_fields)
    def get(self, team_number):
        team = TeamModel.query.filter_by(team_number=team_number).first()
        if not team:
            abort(404, message="The requested team was not found. Please try again.")
        return team

class Events(Resource):
    @marshal_with(event_model_fields)
    def get(self):
        return EventModel.query.all()

class Event(Resource):
    @marshal_with(event_model_fields)
    def get(self, event_code):
        event = EventModel.query.filter_by(event_code=event_code).first()
        if not event:
            abort(404, message="The requested event could not be found. Please try again.")
        return event

@app.route('/api')
def index():
    return render_template('index.html')

@app.route('/api/events/calculate')
def update_events():
    with app.app_context():
        events = get_all_events()

        with db.session.no_autoflush:
            for event in events:
                model_obj = EventModel(event)
                query: EventModel = EventModel.query.filter_by(event_code=event.event_code).first()

                if not query:
                    print(f"Found new event ({event.event_code}), adding to database.")
                    db.session.add(model_obj)
                else:
                    print(f"Updating existing team. ({event.event_code})")
                    query.update(event)

        db.session.commit()
        print("All changes comitted.")
    return "", 204

@app.route('/api/teams/calculate')
def update_teams():
    with app.app_context():
        #Calculate all statistics
        teams = calculate_all_stats()

        # Loop through all teams and add/update teams
        with db.session.no_autoflush:
            for team in teams.values():
                model_obj = TeamModel(team)
                query: TeamModel = TeamModel.query.filter_by(team_number=team.team_number).first()

                if not query:
                    print(f"Found new team ({team.team_number}), adding to database.")
                    db.session.add(model_obj)
                else:
                    print(f"Updating existing team. ({team.team_number})")
                    query.update(team)

        db.session.commit()
        print("All changes comitted.")
    return "", 204

@app.route('/api/cron/update')
def update_daily():
    with app.app_context():
        metadata = AppMetaData.query.get(0)
        last_updated = metadata.last_updated
        new_events, teams = update_teams_to_date(last_updated)

        with db.session.no_autoflush:
            for event in new_events:
                event_obj = EventObj(event)
                model_obj = EventModel(event_obj)
                query: EventModel = EventModel.query.filter_by(event_code=event_obj.event_code).first()

                if not query:
                    print(f"Found new event ({event_obj.event_code}), adding to database.")
                    db.session.add(model_obj)
                else:
                    print(f"Updating existing team. ({event_obj.event_code})")
                    query.update(event_obj)

            for team in teams.values():
                model_obj = TeamModel(team)
                query: TeamModel = TeamModel.query.filter_by(team_number=team.team_number).first()

                if not query:
                    print(f"Found new team ({team.team_number}), adding to database.")
                    db.session.add(model_obj)
                else:
                    print(f"Updating existing team. ({team.team_number})")
                    query.update(team)

        metadata.last_updated = datetime.datetime.now()
        db.session.commit()
    return "", 204

api.add_resource(Teams, '/api/teams/')
api.add_resource(Team, '/api/teams/<int:team_number>/')
api.add_resource(Events, '/api/events/')
api.add_resource(Event, '/api/events/<string:event_code>/')
api.add_resource(MetaData, '/api/info/')