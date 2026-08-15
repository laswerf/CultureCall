import requests

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def pts(value):
    """Format value as abbreviated pts."""
    value = float(value)

    if abs(value) >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f} trillion pts"
    elif abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} billion pts"
    elif abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f} million pts"
    else:
        return f"{value:,.2f} pts"

def formatNum(value):
    value = float(value)

    if abs(value) >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f} trillion"
    elif abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} billion"
    elif abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f} million"
    else:
        return f"{value:,.2f}"