from flask import *
from require_signin import *
import sqlite3 as sql
import config
import models.graph as graph
import models.regression as regression
import models.question as question
from dashboard import get_data

blueprint = Blueprint('testing', __name__)

@blueprint.route('/', methods=['GET', 'POST'])
@require_signin
def _index():
	skill = request.form["skill"]
	if "answer" in request.form:
		flag = regression.submit_answer(request.form["student_id"], request.form["problem_id"], request.form["qq"], skill)
		json = question.getJSON(session["username"], skill, False, flag, request.form["problem_id"])
	else:
		json = question.getJSON(session['username'], skill, True)
	return render_template('testing.html', username = session.get('username', None), q = json, s = skill)