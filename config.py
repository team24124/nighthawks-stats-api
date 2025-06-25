import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_POSTGRES_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False