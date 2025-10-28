from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from scripts.models import get_tests, add_test, delete_test

water_tests_bp = Blueprint("water_tests_bp", __name__)

def login_required(f):
    from functools import wraps
    from flask import redirect, url_for
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth_bp.login"))
        return f(*args, **kwargs)
    return decorated

@water_tests_bp.route("/tanks/<int:tank_id>")
@login_required
def view_tank(tank_id):
    tests = get_tests(tank_id)
    return render_template("view_tank.html", tank_id=tank_id, tests=tests)

@water_tests_bp.route("/tanks/<int:tank_id>/tests/add", methods=["GET", "POST"])
@login_required
def add_test_route(tank_id):
    if request.method == "POST":
        data = {
            "date_observed": request.form.get("date_observed", "").strip(),
            "ammonia": float(request.form.get("ammonia") or 0),
            "nitrite": float(request.form.get("nitrite") or 0),
            "nitrate": float(request.form.get("nitrate") or 0),
            "ph": float(request.form.get("ph") or 0),
            "salinity": float(request.form.get("salinity") or 0),
            "temperature": float(request.form.get("temperature") or 0),
            "phosphate": float(request.form.get("phosphate") or 0),
            "calcium": float(request.form.get("calcium") or 0),
            "notes": request.form.get("notes", "").strip()
        }
        add_test(tank_id, data)
        flash("Test saved.")
        return redirect(url_for("water_tests_bp.view_tank", tank_id=tank_id))
    return render_template("add_test.html", tank_id=tank_id)
