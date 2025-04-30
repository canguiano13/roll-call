from flask import Blueprint, render_template, flash, redirect
from extensions import login_manager

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@errors_bp.app_errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400

@login_manager.unauthorized_handler
def unauthorized():
    flash("Sorry. You're not authorized to do that. Sign in or switch accounts.", category='error')
    return redirect('/login')
