"""Small reusable decorators for routes."""

from functools import wraps

from flask import session, redirect, url_for


def login_required(view):
    # Put @login_required above any route that should only work for
    # someone who is already logged in. If nobody is logged in, this
    # sends them to the login page instead of running the real route.
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped
