from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

def init_auth(mysql):
    @auth_bp.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for("dashboard.dashboard"))
            else:
                flash("Incorrect username or password.")
                return render_template("login.html")

        return render_template("login.html")

    @auth_bp.route("/signup", methods=["GET", "POST"])
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
            except Exception:
                mysql.connection.rollback()
                flash("Username already exists or error creating account.")
                cursor.close()
                return render_template("signup.html")

            cursor.close()
            flash("Account created. Please log in.")
            return redirect(url_for("auth.login"))

        return render_template("signup.html")

    @auth_bp.route("/logout")
    def logout():
        session.clear()
        flash("Logged out.")
        return redirect(url_for("auth.login"))