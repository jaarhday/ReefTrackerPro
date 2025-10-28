from flask import Flask
from scripts.config import Config
from scripts.models import mysql
from scripts.auth import auth_bp
from scripts.dashboard import dashboard_bp
from scripts.water_tests import water_tests_bp

app = Flask(__name__)
app.config.from_object(Config)

mysql.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(water_tests_bp)

if __name__ == "__main__":
    app.run(debug=True)
