import os
from flask import Flask
from flask_mysql_connector import MySQL
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# configuration class for the Flask app
class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET", "replace-this-secret")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "reef_tracker")

# creates and configures the Flask app and MySQL connection
def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "../templates"))
    app.secret_key = Config.SECRET_KEY
    app.config['MYSQL_HOST'] = Config.MYSQL_HOST
    app.config['MYSQL_USER'] = Config.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
    app.config['MYSQL_DATABASE'] = Config.MYSQL_DATABASE

    mysql = MySQL(app)
    return app, mysql