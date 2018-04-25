import re

from flask import *

import models.user as user

blueprint = Blueprint('users', __name__)

re_username = re.compile(r'^[a-zA-Z0-9_]+$');
re_password = re.compile(r'^[a-zA-Z0-9_]+$');

def _signup_validate(request):
    form = request.form
    if 'username' not in form:
        return False
    if 'usertype' not in form:
        return False
    if 'password' not in form:
        return False
    if 'password2' not in form:
        return False
    un0 = form['username']
    pw0 = form['password']
    pw1 = form['password2']
    if len(un0) < 6 or len(un0) > 15:
        return False
    if len(pw0) < 6 or len(pw0) > 15:
        return False
    if len(pw1) < 6 or len(pw1) > 15:
        return False
    if re_username.match(form['username']) is None:
        return False
    if re_password.match(form['password']) is None:
        return False
    if pw0 != pw1:
        return False
    return True

def _signin_validate(request):
    form = request.form
    if 'username' not in form:
        return False
    if 'password' not in form:
        return False
    un0 = form['username']
    pw0 = form['password']
    if len(un0) < 6 or len(un0) > 15:
        return False
    if len(pw0) < 6 or len(pw0) > 15:
        return False
    if re_username.match(form['username']) is None:
        return False
    if re_password.match(form['password']) is None:
        return False
    return True

@blueprint.route('/new', methods=['GET', 'POST'])
def _signup():
    if request.method == 'GET':
        return render_template('signup.html', alert=None)
    if not _signup_validate(request):
        return render_template('signup.html', alert='error', message='Invalid username and/or password.') 
    form = request.form
    user.create_user(form['username'], form['password'], form['usertype'])
    res = make_response(redirect('/dashboard'))
    session['username'] = form['username']
    return res

@blueprint.route('/signin', methods=['GET', 'POST'])
def _signin():
    if request.method == 'GET':
        if 'username' in session:
            return redirect('/dashboard')
        render_template('index.html', alert=None, message=None)
    if not _signin_validate(request):
        return render_template('index.html', alert='error', message='Invalid username and/or password.') 
    if 'username' in session:
        return redirect('/dashboard')
    form = request.form
    result = user.check_credentials(form['username'], form['password'])
    if result == False:
        return render_template('index.html', alert='error', message='Unknown username and/or incorrect password.') 
    res = make_response(redirect('/dashboard'))
    session['username'] = form['username']
    return res