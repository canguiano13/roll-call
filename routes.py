#defines the routes for the application
from flask import Blueprint, Response, render_template
from models import User, Guestbook, Message
from db import db

#set this as a blueprint
routes = Blueprint("routes", __name__, template_folder="templates")

#define routes
@routes.route('/')
def index():
    return "hello"

@routes.route('/signin')
def signin():
    return render_template('signin.html')

@routes.route('/createEvent')
def create_event():
    return render_template('createEvent.html')

@routes.route('/testhome')
def testhome():
    return render_template("testhome.html")

@routes.route('/allusers', methods=["GET"])
def getallusers():
    users = db.session.query(User).all()
    user_list = "\n".join(f"{user.first_name} {user.last_name}: {user.email}" for user in users)
    return Response(user_list, mimetype="text/plain")

@routes.route('/allguestbooks', methods=["GET"])
def getallguestbooks():
    guestbooks = db.session.query(Guestbook).all()
    guestbook_list = "\n".join(f"EVENT {gb.event_title} ({gb.event_date}) happening at: {gb.event_address}" for gb in guestbooks)
    return Response(guestbook_list, mimetype="text/plain")

@routes.route('/allmessages', methods=["GET"])
def getallmessages():
    messages = db.session.query(Message).all()
    message_list = "\n".join(f"{msg.display_name} says: {msg.message_content}" for msg in messages)
    return Response(message_list, mimetype="text/plain")
