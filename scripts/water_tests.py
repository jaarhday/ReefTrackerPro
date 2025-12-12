from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from scripts.models import login_required

# creates the water tests blueprint
water_bp = Blueprint("water_tests", __name__)

def init_water_tests(mysql):
    @water_bp.route("/tanks/<int:tank_id>")
    @login_required
    # displays the tank details and its water tests
    def view_tank(tank_id):
        cursor = mysql.connection.cursor()
        # retrieves tank info and its water tests
        cursor.execute("SELECT * FROM tanks WHERE tank_id = %s AND user_id = %s", (tank_id, session["user_id"]))
        tank = cursor.fetchone()
        
        # if tank not found or not owned by user, redirect
        cursor.execute("SELECT * FROM water_tests WHERE tank_id = %s", (tank_id,))
        tests = cursor.fetchall()
        cursor.close()

        return render_template("view_tank.html", tank=tank, tests=tests, tank_id=tank_id)

    @water_bp.route("/tanks/<int:tank_id>/tests/add", methods=["GET", "POST"])
    @login_required
    # adds a new water test for the specified tank
    def add_test(tank_id):
        cursor = mysql.connection.cursor()
        # verify tank ownership
        cursor.execute("SELECT tank_id FROM tanks WHERE tank_id=%s AND user_id=%s", (tank_id, session["user_id"]))
        ok = cursor.fetchone()
        cursor.close()
        # if tank not found or not owned by user, redirect
        if not ok:
            flash("Tank not found or not yours.")
            return redirect(url_for("dashboard.dashboard"))
        
        if request.method == "POST":
            # process form submission
            date_observed = request.form.get("date_observed", "").strip()
            if not date_observed:
                flash("Date observed is required.")
                return render_template("add_test.html", tank_id=tank_id)

            # simple float parser with error handling
            def parse_float(s, field):
                if s == "":
                    return None
                try:
                    return float(s)
                except:
                    raise ValueError(f"{field} must be a number.")

            try:
                # parse all numeric fields
                values = {field: parse_float(request.form.get(field, ""), field.capitalize())
                          for field in ["ammonia", "nitrite", "nitrate", "ph", "salinity", "temperature", "phosphate", "calcium"]}
            except ValueError as e:
                flash(str(e))
                return render_template("add_test.html", tank_id=tank_id)
            
            notes = request.form.get("notes", "").strip()
            cursor = mysql.connection.cursor()
            # insert new water test into database
            cursor.execute("""INSERT INTO water_tests
                (tank_id, user_id, date_observed, ammonia, nitrite, nitrate, ph, salinity, temperature, phosphate, calcium, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (tank_id, session["user_id"], date_observed, values["ammonia"], values["nitrite"], values["nitrate"],
                 values["ph"], values["salinity"], values["temperature"], values["phosphate"], values["calcium"], notes))
            mysql.connection.commit()
            cursor.close()
            flash("Test saved.")
            return redirect(url_for("water_tests.view_tank", tank_id=tank_id))

        return render_template("add_test.html", tank_id=tank_id)
    
    @water_bp.route("/tests/<int:test_id>/edit", methods=["GET", "POST"])
    @login_required
    # edits an existing water test
    def edit_test(test_id):
        cursor = mysql.connection.cursor()

        # get the test and ensure the user owns the tank
        cursor.execute("""
            SELECT wt.water_test_id, wt.tank_id, wt.date_observed, wt.ammonia, wt.nitrite,
                wt.nitrate, wt.ph, wt.salinity, wt.temperature, wt.phosphate,
                wt.calcium, wt.notes
            FROM water_tests wt
            JOIN tanks t ON wt.tank_id = t.tank_id
            WHERE wt.water_test_id = %s AND t.user_id = %s
        """, (test_id, session["user_id"]))

        row = cursor.fetchone()
        if not row:
            cursor.close()
            flash("You do not have permission to edit this test.")
            return redirect(url_for("dashboard.dashboard"))

        # convert tuple to dictionary for template
        test = {
            "water_test_id": row[0],
            "tank_id": row[1],
            "date_observed": row[2],
            "ammonia": row[3],
            "nitrite": row[4],
            "nitrate": row[5],
            "ph": row[6],
            "salinity": row[7],
            "temperature": row[8],
            "phosphate": row[9],
            "calcium": row[10],
            "notes": row[11]
        }

        # handle form submission
        if request.method == "POST":
            date_observed = request.form.get("date_observed", "").strip()

            # simple float parser
            def get_float(field):
                val = request.form.get(field, "").strip()
                return float(val) if val else None

            try:
                # parse all numeric fields
                ammonia = get_float("ammonia")
                nitrite = get_float("nitrite")
                nitrate = get_float("nitrate")
                ph = get_float("ph")
                salinity = get_float("salinity")
                temperature = get_float("temperature")
                phosphate = get_float("phosphate")
                calcium = get_float("calcium")
            except:
                flash("All number fields must be valid numbers.")
                return render_template("edit_test.html", test=test, tank_id=test["tank_id"])

            notes = request.form.get("notes", "").strip()

            # update the database
            cursor.execute("""
                UPDATE water_tests SET
                    date_observed=%s, ammonia=%s, nitrite=%s, nitrate=%s,
                    ph=%s, salinity=%s, temperature=%s, phosphate=%s,
                    calcium=%s, notes=%s
                WHERE water_test_id=%s
            """, (
                date_observed, ammonia, nitrite, nitrate, ph, salinity,
                temperature, phosphate, calcium, notes, test_id
            ))
            mysql.connection.commit()
            cursor.close()

            flash("Test updated.")
            return redirect(url_for("water_tests.view_tank", tank_id=test["tank_id"]))

        cursor.close()
        return render_template("edit_test.html", test=test, tank_id=test["tank_id"])


    @water_bp.route("/tests/<int:test_id>/delete")
    @login_required
    def delete_test(test_id):
        # only delete if test belongs to a tank owned by the user
        cursor = mysql.connection.cursor()
        cursor.execute("""DELETE wt FROM water_tests wt
                        JOIN tanks t ON wt.tank_id = t.tank_id
                        WHERE wt.water_test_id = %s AND t.user_id = %s""",
                    (test_id, session["user_id"]))
        mysql.connection.commit()
        cursor.close()
        flash("Test deleted.")
        return redirect(url_for("dashboard.dashboard"))
