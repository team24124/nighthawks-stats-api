import logging

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

api = Api(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models

if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)

app.logger.setLevel(logging.INFO)
app.logger.info("App started.")