from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from scripts.models import login_required

water_bp = Blueprint("water_tests", __name__)

def init_water_tests(mysql):
    @water_bp.route("/tanks/<int:tank_id>")
    @login_required
    def view_tank(tank_id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tanks WHERE tank_id = %s AND user_id = %s", (tank_id, session["user_id"]))
        tank = cursor.fetchone()

        cursor.execute("SELECT * FROM water_tests WHERE tank_id = %s", (tank_id,))
        tests = cursor.fetchall()
        cursor.close()

        return render_template("view_tank.html", tank=tank, tests=tests, tank_id=tank_id)

    @water_bp.route("/tanks/<int:tank_id>/tests/add", methods=["GET", "POST"])
    @login_required
    def add_test(tank_id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT tank_id FROM tanks WHERE tank_id=%s AND user_id=%s", (tank_id, session["user_id"]))
        ok = cursor.fetchone()
        cursor.close()
        if not ok:
            flash("Tank not found or not yours.")
            return redirect(url_for("dashboard.dashboard"))

        if request.method == "POST":
            date_observed = request.form.get("date_observed", "").strip()
            if not date_observed:
                flash("Date observed is required.")
                return render_template("add_test.html", tank_id=tank_id)

            def parse_float(s, field):
                if s == "":
                    return None
                try:
                    return float(s)
                except:
                    raise ValueError(f"{field} must be a number.")

            try:
                values = {field: parse_float(request.form.get(field, ""), field.capitalize())
                          for field in ["ammonia", "nitrite", "nitrate", "ph", "salinity", "temperature", "phosphate", "calcium"]}
            except ValueError as e:
                flash(str(e))
                return render_template("add_test.html", tank_id=tank_id)

            notes = request.form.get("notes", "").strip()
            cursor = mysql.connection.cursor()
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
    def edit_test(test_id):
        # fetch test and verify ownership via join
        cursor = mysql.connection.cursor()
        cursor.execute("""SELECT wt.water_test_id, wt.date_observed, wt.ammonia, wt.nitrite, wt.nitrate, wt.ph, wt.salinity,
                            wt.temperature, wt.phosphate, wt.calcium, wt.notes,  wt.tank_id
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
            return redirect(url_for("view_tank", tank_id=row[11]))  # tank_id is last in select

        cursor.close()
        return render_template("edit_test.html", test=row)

    @water_bp.route("/tests/<int:test_id>/delete")
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
        return redirect(url_for("dashboard.dashboard"))
