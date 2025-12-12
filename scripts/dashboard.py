from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from scripts.models import login_required, get_user

# creates the dashboard blueprint
dashboard_bp = Blueprint("dashboard", __name__)

# initializes the dashboard routes
def init_dashboard(mysql):
    @dashboard_bp.route("/dashboard")
    @login_required
    # displays the user's dashboard with their tanks
    def dashboard():
        user = get_user()
        cursor = mysql.connection.cursor()
        # retrieves tanks for the logged-in user
        cursor.execute("SELECT tank_id, tank_name, tank_size, tanks_type, created_at FROM tanks WHERE user_id=%s ORDER BY created_at DESC", (user["user_id"],))
        tanks = cursor.fetchall()
        cursor.close()
        return render_template("dashboard.html", user=user, tanks=tanks)

    # route to add a new tank
    @dashboard_bp.route("/tanks/add", methods=["GET", "POST"])
    @login_required
    def add_tank():
        if request.method == "POST":
            name = request.form.get("tank_name", "").strip()
            size = request.form.get("tank_size", "").strip()
            tanks_type = request.form.get("tanks_type", "").strip()

            if not name:
                flash("Tank name is required.")
                return render_template("add_tank.html")

            try:
                size_val = int(size) if size else None
            except ValueError:
                flash("Tank size must be a whole number.")
                return render_template("add_tank.html")

            cursor = mysql.connection.cursor()
            # inserts the new tank into the database
            cursor.execute("INSERT INTO tanks (user_id, tank_name, tank_size, tanks_type) VALUES (%s,%s,%s,%s)",
                           (session["user_id"], name, size_val, tanks_type))
            mysql.connection.commit()
            cursor.close()
            flash("Tank added.")
            return redirect(url_for("dashboard.dashboard"))

        return render_template("add_tank.html")

    @dashboard_bp.route("/tanks/<int:tank_id>/delete")
    @login_required
    def delete_tank(tank_id):
        cursor = mysql.connection.cursor()
        # deletes the specified tank if it belongs to the logged-in user
        cursor.execute("DELETE FROM tanks WHERE tank_id=%s AND user_id=%s", (tank_id, session["user_id"]))
        mysql.connection.commit()
        cursor.close()
        flash("Tank deleted.")
        return redirect(url_for("dashboard.dashboard"))