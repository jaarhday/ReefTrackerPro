from flask import Blueprint, render_template, redirect, url_for, session, flash
from scripts.models import get_tanks, add_tank, delete_tank

dashboard_bp = Blueprint("dashboard_bp", __name__)

def login_required(f):
    from functools import wraps
    from flask import redirect, url_for
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth_bp.login"))
        return f(*args, **kwargs)
    return decorated

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    tanks = get_tanks(user_id)
    return render_template("dashboard.html", user=session, tanks=tanks)

@dashboard_bp.route("/tanks/add", methods=["GET", "POST"])
@login_required
def add_tank_route():
    from flask import request
    if request.method == "POST":
        name = request.form.get("tank_name", "").strip()
        volume = request.form.get("tank_volume", "").strip()
        tank_type = request.form.get("tank_type", "").strip()
        volume_val = int(volume) if volume else None
        add_tank(session["user_id"], name, volume_val, tank_type)
        flash("Tank added.")
        return redirect(url_for("dashboard_bp.dashboard"))
    return render_template("add_tank.html")

@dashboard_bp.route("/tanks/<int:tank_id>/delete")
@login_required
def delete_tank_route(tank_id):
    delete_tank(tank_id, session["user_id"])
    flash("Tank deleted.")
    return redirect(url_for("dashboard_bp.dashboard"))