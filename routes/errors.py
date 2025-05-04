from flask import Blueprint, render_template, flash, redirect
from extensions import login_manager


errors = Blueprint('errors', __name__)

#render HTML template for 400 (bad request) errors
@errors.app_errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400

#render HTML template for 403 (unauthorized) errors
@errors.app_errorhandler(403)
def unauthorized_error(error):
    return render_template('403.html'), 403

#render HTML template for 404 (page not found) errors
@errors.app_errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

#render HTML template for 500 (internal) errors
@errors.app_errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

#handles errors related to unauthorized user actions
@login_manager.unauthorized_handler
def unauthorized():
    flash("Sorry, you need to sign in before you can do that.", category='error')
    return redirect('/login')
