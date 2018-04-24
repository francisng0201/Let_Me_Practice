from functools import wraps
from flask import g, request, redirect, url_for, session

def require_signin(route):
    @wraps(route)
    def fn(*args, **kwargs):
        if 'username' not in session:
            return redirect('/users/signin?prompt=true')
        return route(*args, **kwargs)
    return fn