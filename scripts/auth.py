from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from scripts.models import get_user_by_username, create_user

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Please enter username and password.")
            return render_template("login.html")

        row = get_user_by_username(username)
        if row and check_password_hash(row[1], password):
            session["user_id"] = row[0]
            session["username"] = username
            return redirect(url_for("dashboard_bp.dashboard"))
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
        try:
            create_user(username, pw_hash)
        except:
            flash("Username already exists or error creating account.")
            return render_template("signup.html")

        flash("Account created. Please log in.")
        return redirect(url_for("auth_bp.login"))

    return render_template("signup.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("auth_bp.login"))