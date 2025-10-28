# app.py
import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysql_connector import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------- Configuration -------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "replace-this-secret")

# MySQL config - change these to match your local MySQL
app.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST", "localhost")
app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER", "root")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD", "")
app.config['MYSQL_DATABASE'] = os.environ.get("MYSQL_DATABASE", "reef_tracker")

mysql = MySQL(app)

# ------------------- Helpers -------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def get_user():
    if "user_id" in session:
        return {"user_id": session["user_id"], "username": session.get("username")}
    return None

# ------------------- Routes -------------------
@app.route("/")
def root():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# -------- Auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter username and password.")
            return render_template("login.html")

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT user_id, password FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        cursor.close()

        if row and check_password_hash(row[1], password):
            session["user_id"] = row[0]
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Incorrect username or password.")
            return render_template("login.html")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide username and password.")
            return render_template("signup.html")

        pw_hash = generate_password_hash(password)
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s,%s)", (username, pw_hash))
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            flash("Username already exists or error creating account.")
            cursor.close()
            return render_template("signup.html")
        cursor.close()
        flash("Account created. Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("login"))

# -------- Dashboard & Tanks ----------
@app.route("/dashboard")
@login_required
def dashboard():
    user = get_user()
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT tank_id, tank_name, tank_size, tanks_type, created_at FROM tanks WHERE user_id=%s ORDER BY created_at DESC", (user["user_id"],))
    tanks = cursor.fetchall()
    cursor.close()
    return render_template("dashboard.html", user=user, tanks=tanks)

@app.route("/tanks/add", methods=["GET", "POST"])
@login_required
def add_tank():
    if request.method == "POST":
        name = request.form.get("tank_name", "").strip()
        size = request.form.get("tank_size", "").strip()
        tanks_type = request.form.get("tanks_type", "").strip()  # free text per your choice C

        if not name:
            flash("Tank name is required.")
            return render_template("add_tank.html")

        # convert volume to int if neccessary
        size_val = None
        try:
            size_val = int(size) if size else None
        except ValueError:
            flash("Tank size(volume) must be a whole number (gallons or liters).")
            return render_template("add_tank.html")

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO tanks (user_id, tank_name, tank_size, tanks_type) VALUES (%s,%s,%s,%s)",
                       (session["user_id"], name, size_val, tanks_type))
        mysql.connection.commit()
        cursor.close()
        flash("Tank added.")
        return redirect(url_for("dashboard"))

    return render_template("add_tank.html")

@app.route("/tanks/<int:tank_id>/delete")
@login_required
def delete_tank(tank_id):
    # only delete if tank belongs to user
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM tanks WHERE tank_id=%s AND user_id=%s", (tank_id, session["user_id"]))
    mysql.connection.commit()
    cursor.close()
    flash("Tank deleted.")
    return redirect(url_for("dashboard"))

# -------- Water Tests ----------
@app.route("/tanks/<int:tank_id>")
@login_required
def view_tank(tank_id):
    # ensure tank belongs to user
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT tank_id, tank_name FROM tanks WHERE tank_id=%s AND user_id=%s", (tank_id, session["user_id"]))
    tank = cursor.fetchone()
    if not tank:
        cursor.close()
        flash("Tank not found.")
        return redirect(url_for("dashboard"))

    # fetch tests
    cursor.execute("""SELECT water_test_id, date_observed, ammonia, nitrite, nitrate, ph, salinity, temperature, phosphate, calcium, notes
                      FROM water_tests WHERE tank_id=%s ORDER BY date_observed DESC""", (tank_id,))
    tests = cursor.fetchall()
    cursor.close()
    return render_template("view_tank.html", tank=tank, tests=tests)

@app.route("/tanks/<int:tank_id>/tests/add", methods=["GET", "POST"])
@login_required
def add_test(tank_id):
    # verify tank belongs to user
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT tank_id FROM tanks WHERE tank_id=%s AND user_id=%s", (tank_id, session["user_id"]))
    ok = cursor.fetchone()
    cursor.close()
    if not ok:
        flash("Tank not found or not yours.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # required fields and basic validation
        date_observed = request.form.get("date_observed", "").strip()
        ammonia = request.form.get("ammonia", "").strip()
        nitrite = request.form.get("nitrite", "").strip()
        nitrate = request.form.get("nitrate", "").strip()
        ph = request.form.get("ph", "").strip()
        salinity = request.form.get("salinity", "").strip()
        temperature = request.form.get("temperature", "").strip()
        phosphate = request.form.get("phosphate", "").strip()
        calcium = request.form.get("calcium", "").strip()
        notes = request.form.get("notes", "").strip()

        # Validate required fields
        if not date_observed:
            flash("Date observed is required.")
            return render_template("add_test.html", tank_id=tank_id)

        # helper to parse floats
        def parse_float(s, field):
            if s == "":
                return None
            try:
                return float(s)
            except:
                raise ValueError(f"{field} must be a number.")

        try:
            ammonia_v = parse_float(ammonia, "Ammonia")
            nitrite_v = parse_float(nitrite, "Nitrite")
            nitrate_v = parse_float(nitrate, "Nitrate")
            ph_v = parse_float(ph, "pH")
            salinity_v = parse_float(salinity, "Salinity")
            temperature_v = parse_float(temperature, "Temperature")
            phosphate_v = parse_float(phosphate, "Phosphate")
            calcium_v = parse_float(calcium, "Calcium")
        except ValueError as e:
            flash(str(e))
            return render_template("add_test.html", tank_id=tank_id)

        # Insert
        cursor = mysql.connection.cursor()
        cursor.execute("""INSERT INTO water_tests
            (tank_id, user_id, date_observed, ammonia, nitrite, nitrate, ph, salinity, temperature, phosphate, calcium, notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (tank_id, session["user_id"], date_observed, ammonia_v, nitrite_v, nitrate_v, ph_v, salinity_v, temperature_v, phosphate_v, calcium_v, notes))

        mysql.connection.commit()
        cursor.close()
        flash("Test saved.")
        return redirect(url_for("view_tank", tank_id=tank_id))

    return render_template("add_test.html", tank_id=tank_id)

@app.route("/tests/<int:test_id>/edit", methods=["GET", "POST"])
@login_required
def edit_test(test_id):
    # fetch test and verify ownership via join
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT wt.water_test_id, wt.tank_id, wt.date_observed, wt.ammonia, wt.nitrite, wt.nitrate, wt.ph, wt.salinity,
                         wt.temperature, wt.phosphate, wt.calcium, wt.notes
                  FROM water_tests wt
                  JOIN tanks t ON wt.tank_id = t.tank_id
                  WHERE wt.water_test_id=%s AND t.user_id=%s""", (test_id, session["user_id"]))

    row = cursor.fetchone()
    if not row:
        cursor.close()
        flash("Test not found or not allowed.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        date_observed = request.form.get("date_observed", "").strip()
        ammonia = request.form.get("ammonia", "").strip()
        nitrite = request.form.get("nitrite", "").strip()
        nitrate = request.form.get("nitrate", "").strip()
        ph = request.form.get("ph", "").strip()
        salinity = request.form.get("salinity", "").strip()
        temperature = request.form.get("temperature", "").strip()
        phosphate = request.form.get("phosphate", "").strip()
        calcium = request.form.get("calcium", "").strip()
        notes = request.form.get("notes", "").strip()

        def parse_float(s, field):
            if s == "":
                return None
            try:
                return float(s)
            except:
                raise ValueError(f"{field} must be a number.")

        try:
            ammonia_v = parse_float(ammonia, "Ammonia")
            nitrite_v = parse_float(nitrite, "Nitrite")
            nitrate_v = parse_float(nitrate, "Nitrate")
            ph_v = parse_float(ph, "pH")
            salinity_v = parse_float(salinity, "Salinity")
            temperature_v = parse_float(temperature, "Temperature")
            phosphate_v = parse_float(phosphate, "Phosphate")
            calcium_v = parse_float(calcium, "Calcium")
        except ValueError as e:
            flash(str(e))
            return render_template("edit_test.html", test=row)

        cursor.execute("""UPDATE water_tests SET date_observed=%s, ammonia=%s, nitrite=%s, nitrate=%s,
                          ph=%s, salinity=%s, temperature=%s, phosphate=%s, calcium=%s, notes=%s
                          WHERE water_test_id=%s""",
                       (date_observed, ammonia_v, nitrite_v, nitrate_v, ph_v, salinity_v, temperature_v, phosphate_v, calcium_v, notes, test_id))
        mysql.connection.commit()
        cursor.close()
        flash("Test updated.")
        return redirect(url_for("view_tank", tank_id=row[1]))

    cursor.close()
    return render_template("edit_test.html", test=row)

@app.route("/tests/<int:test_id>/delete")
@login_required
def delete_test(test_id):
    # Only delete if test belongs to a tank owned by the user
    cursor = mysql.connection.cursor()
    cursor.execute("""DELETE wt FROM water_tests wt
                      JOIN tanks t ON wt.tank_id = t.tank_id
                      WHERE wt.water_test_id = %s AND t.user_id = %s""",
                   (test_id, session["user_id"]))
    mysql.connection.commit()
    cursor.close()
    flash("Test deleted (if it belonged to you).")
    return redirect(url_for("dashboard"))

# ------------------- Run -------------------
if __name__ == "__main__":
    app.run(debug=True)
