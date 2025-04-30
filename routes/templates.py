from flask import Blueprint, render_template
from flask_login import login_required

templates_bp = Blueprint('templates', __name__)

@templates_bp.route('/createBirthday')
@login_required
def create_birthday():
    return render_template('createBirthday.html')

@templates_bp.route('/createChristmas')
@login_required
def create_christmas():
    return render_template('createChristmas.html')

@templates_bp.route('/createHalloween')
@login_required
def create_halloween():
    return render_template('createHalloween.html')

@templates_bp.route('/createStPatty')
@login_required
def create_stpatty():
    return render_template('createStPatty.html')
