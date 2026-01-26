import datetime

from flask import render_template
from flask_restful import Resource, marshal_with, abort
from app.models import TeamModel, team_model_fields, event_model_fields, EventModel, AppMetaData, meta_data_fields

from app import app, api, db
from stats.data import parse_date
from stats.events import get_all_events, Event as EventObj, event_has_teams, get_event_by_code
from stats.calculations import calculate_all_stats, update_teams_to_date
from app.models import PendingEventModel

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
        print("Hard reset: deleting all event data")

        # 1. DELETE EVERYTHING
        db.session.query(EventModel).delete()
        db.session.query(PendingEventModel).delete()
        db.session.commit()

        print("All event tables cleared")

        # 2. FETCH ALL EVENTS
        events = get_all_events()
        seen_codes: set[str] = set()

        processed = 0

        for event in events:
            code = event.event_code

            # Deduplicate correctly
            if code in seen_codes:
                continue
            seen_codes.add(code)

            if event_has_teams(code):
                db.session.add(EventModel(event))
            else:
                db.session.add(
                    PendingEventModel(
                        event_code=code,
                        first_seen=datetime.datetime.utcnow(),
                        last_checked=datetime.datetime.utcnow()
                    )
                )
                print(f"{event} has no teams")

            processed += 1
            if processed % 25 == 0:
                db.session.commit()

        db.session.commit()
        print("Full rebuild complete")

    return "", 204

@app.route('/api/teams/calculate')
def update_teams():
    with app.app_context():
        print("Hard reset: recalculating all teams")

        db.session.query(TeamModel).delete()
        db.session.commit()

        teams = calculate_all_stats()

        for team in teams.values():
            db.session.add(TeamModel(team))

        db.session.commit()
        print("Team rebuild complete")

    return "", 204


@app.route('/api/cron/update')
def update_daily():
    with app.app_context():

        # 1. Load metadata
        metadata = AppMetaData.query.get(0)
        if not metadata:
            metadata = AppMetaData(id=0, last_updated=datetime.datetime.min)
            db.session.add(metadata)
            db.session.commit()
        last_updated = metadata.last_updated

        # 2. Do ALL heavy logic in one place
        valid_events, teams, pending_events = update_teams_to_date(last_updated)
        # 3. Clear pending table
        db.session.query(PendingEventModel).delete()
        # 4. Upsert events
        with db.session.no_autoflush:
            for event in valid_events:
                model = EventModel(event)
                existing = EventModel.query.filter_by(
                    event_code=event.event_code
                ).first()

                if existing:
                    existing.update(event)
                else:
                    db.session.add(model)

            # 5. Insert still-pending events
            for event in pending_events:
                db.session.add(PendingEventModel(
                    event_code=event.event_code,
                    first_seen=datetime.datetime.utcnow(),
                    last_checked=datetime.datetime.utcnow()
                ))
            # 6. Upsert teams
            for team in teams.values():
                model = TeamModel(team)
                existing = TeamModel.query.filter_by(
                    team_number=team.team_number
                ).first()

                if existing:
                    existing.update(team)
                else:
                    db.session.add(model)

        # 7. Update metadata
        metadata.last_updated = datetime.datetime.utcnow()
        db.session.commit()

    return "", 204




def process_pending_events():
    pending_events = PendingEventModel.query.all()

    for pending in pending_events:
        if not event_has_teams(pending.event_code):
            pending.last_checked = datetime.datetime.utcnow()
            continue

        event = get_event_by_code(event_code=pending.event_code)
        if event is None:
            continue

        event_obj = EventObj(event[0])
        model_obj = EventModel(event_obj)

        query = EventModel.query.filter_by(event_code=event_obj.event_code).first()
        if not query:
            db.session.add(model_obj)
        else:
            query.update(event_obj)

        db.session.delete(pending)


api.add_resource(Teams, '/api/teams/')
api.add_resource(Team, '/api/teams/<int:team_number>/')
api.add_resource(Events, '/api/events/')
api.add_resource(Event, '/api/events/<string:event_code>/')
api.add_resource(MetaData, '/api/info/')