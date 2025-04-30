from flask import Blueprint, render_template, redirect, flash
from flask_login import current_user
from datetime import datetime

from models import User, Guestbook, Message


home = Blueprint("home", __name__)

#login is not required for the home page
#will redirect user to the correct template according to authentication status
@home.route('/')
def index():
    #if the user is login, display their guestbooks
    if(current_user.is_authenticated):
        #get the current user's guestbooks
        current_user_id = User.get_id(current_user)
        guestbooks = Guestbook.query.filter_by(owner_id=current_user_id).order_by(Guestbook.event_date).all()
        #split into upcoming and past guestbooks
        now = datetime.now()
        upcoming = [g for g in guestbooks if g.event_date >= now]
        past = [g for g in guestbooks if g.event_date < now]
        return render_template('index.html', upcoming_events=upcoming, past_events=past, now=now)
    #display a welcome message on first visit
    flash('Welcome! Sign in or create an account to get started!', category='success')
    return redirect('/signup')

