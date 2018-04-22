from flask import *

from require_signin import *

blueprint = Blueprint('dashboard', __name__)

@blueprint.route('/', methods=['GET'])
@require_signin
def _index():
    return render_template('dashboard.html', username=session['username'])
