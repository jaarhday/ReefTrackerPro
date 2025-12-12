# imports the tools needed for routes, templates, sessions, and password security.
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# creates the auth blueprint
auth_bp = Blueprint("auth", __name__)

# initializes the authentication routes
def init_auth(mysql):
    @auth_bp.route("/login", methods=["GET", "POST"])
    def login():
        # handles login form submission
        if request.method == "POST":
            # gets username and password from form
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                # prompts user to enter both fields if missing
                flash("Please enter username and password.")
                return render_template("login.html")

            # queries the database for the user
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT user_id, password FROM users WHERE username=%s", (username,))
            row = cursor.fetchone()
            cursor.close()

            # verifies password and logs in user
            if row and check_password_hash(row[1], password):
                session["user_id"] = row[0]
                session["username"] = username
                return redirect(url_for("dashboard.dashboard"))
            else:
                flash("Incorrect username or password.")
                return render_template("login.html")
        
        # displays the login form
        return render_template("login.html")

    # sets up the signup route
    @auth_bp.route("/signup", methods=["GET", "POST"])
    def signup():
        # handles signup form submission
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                flash("Please provide username and password.")
                return render_template("signup.html")

            # creates new user in the database
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

    # sets up the logout route
    @auth_bp.route("/logout")
    def logout():
        session.clear()
        flash("Logged out.")
        return redirect(url_for("auth.login"))