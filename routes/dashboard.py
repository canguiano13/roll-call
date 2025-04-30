from flask import Blueprint, render_template, redirect, flash
from flask_login import login_required, current_user
from models import Guestbook, User
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route('/')
@login_required
def index():
    current_user_id = User.get_id(current_user)
    guestbooks = Guestbook.query.filter_by(owner_id=current_user_id).order_by(Guestbook.event_date).all()
    now = datetime.now()
    upcoming = [g for g in guestbooks if g.event_date >= now]
    past = [g for g in guestbooks if g.event_date < now]
    return render_template('index.html', upcoming_events=upcoming, past_events=past, now=now)
