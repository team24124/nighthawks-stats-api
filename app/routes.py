from flask import render_template
from flask_restful import Resource, marshal_with, abort
from app.models import TeamModel, team_model_fields, event_model_fields, EventModel

from app import app, api, db
from stats.opr_epa import calculate_world_epa_opr


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

@app.route('/api/cron/update')
def update():
    with app.app_context():
        #Calculate all statistics
        teams = calculate_world_epa_opr()

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
    return "", 204

api.add_resource(Teams, '/api/teams/')
api.add_resource(Team, '/api/teams/<int:team_number>/')
api.add_resource(Events, '/api/events')
api.add_resource(Event, '/api/events/<string:event_code>/')