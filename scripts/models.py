from functools import wraps
from flask import session, redirect, url_for

# decorator to ensure user is logged in
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

# utility to get current logged-in user info
def get_user():
    if "user_id" in session:
        return {"user_id": session["user_id"], "username": session.get("username")}
    return None