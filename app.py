from scripts.config import create_app
from scripts.auth import auth_bp, init_auth
from scripts.dashboard import dashboard_bp, init_dashboard
from scripts.water_tests import water_bp, init_water_tests

app, mysql = create_app()

init_auth(mysql)
init_dashboard(mysql)
init_water_tests(mysql)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(water_bp)

@app.route("/")
def root():
    from flask import session, redirect, url_for
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))

if __name__ == "__main__":
    app.run(debug=True)