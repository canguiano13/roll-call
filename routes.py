#defines the routes for the application
from flask import Blueprint, Response, render_template, request, redirect, url_for
from models import User, Guestbook, Message
from db import db

#declare "routes" to be a blueprint holding all of the routes we define
routes = Blueprint("routes", __name__, template_folder="templates")

#DEFINE APP ROUTES
@routes.route('/')
def index():
    return render_template('testhome.html')

#handles new user signups
@routes.route('/signUp')
def signup():
    return render_template("signup.html")
@routes.route('/handleSignUp', methods=["POST"])
def create_user():
    #only want to create user when accessed via POST request
    if request.method == "POST":
        #retrieve parameters here
        form_details = request.form.to_dict()
        print(form_details)

        #TODO hash password here
        #form_details['user-pass'] = hashpassword(form_details['user-pass'])
        event_details=f'''
            NEW USER REQUEST. CREATING USER...\n
            first_name: {form_details['first_name']}\n
            last_name:  {form_details['last_name']}\n
            email:      {form_details['email']}\n
            password:   {form_details['password_hash']}\n
            '''
        #call db function here? e.g.
        #create_user_in_table(firstname=XX, lastname=XX, email=XX, pass=hash(XX))
        
        #then route to success page?
    return Response(event_details, mimetype='text/plain')

#TODO figure out if we can use flask login management library here
#Handles user logins
@routes.route('/signIn')
def signin():
    return render_template('signin.html')
@routes.route('/handleSignIn', methods=["POST"])
def login_user():
    #only want to create user when accessed via POST request
    if request.method == "POST":
        #retrieve parameters here
        form_details = request.form.to_dict()
        print(form_details)
        login_details =f'''
            USER IS LOGGING IN WITH DETAILS...\n
            email:          {form_details['email'] if form_details['email'] else None}\n
            password_hash (attempted) {form_details['password_hash'] if form_details['password_hash'] else None}\n
            '''
    return Response(login_details, mimetype='text/plain')


#creating and handling new event
@routes.route('/createEvent')
def create_event():
    return render_template('createEvent.html')
#For handling request form data we can get the form inputs value by using POST attribute.
@routes.route('/handleCreateEvent', methods=["POST"]) 
def handle_new_event():
    if request.method == "POST":
        #retrieve parameters here
        form_details = request.form.to_dict()
        print(form_details)
        #form into datetime
        event_details=f'''
            NEW EVENT REQUEST... \n
            event_title:        {form_details['event_title']}\n
            event_description:  {form_details['event_address']}\n
            event_datetime:         {form_details['event_date']} \n 
            event_time:         {form_details['event_time']} \n
            '''
    #TODO figure out whether we need to redirect to confirmation page or if we can redirect straight to share page
    #TODO replace 1 with actual event id
    return redirect('/share/1')


#render a custom share page for the event
@routes.route('/share/<event_id>')
def share_event(event_id):
    #first query the name, address, date of the event using passed event id
    event_data = db.session.query(Guestbook).get(event_id)
    #if the event doesn't exist, throw a 404 error
    if event_data is None:
        return render_template("404.html"), 404
    print(event_data)
    return render_template('shareEvent.html', data=event_data)


#TODO define skeleton for event page
# @routes.route('/event/{event-id}', methods=['GET'])
# def render_event_page(event_id):
#     data = db.session.query(Message).filter(Message.event_id == {event_id})
#     return render_template('event.html', data=data)
@routes.route('/event')
def render_event_page():
    return render_template('event.html')

#TODO route new messages to this method. Method will take the form data and push them to the page
@routes.route('/testpostmessage')
def post_message_form():
    return render_template('testpost.html', data=dict(event_id="1"))
#this route will be used to populate the database with incoming messages for a specific event page
#TODO fix query for posting message to database
#TODO will need to pass the event id when we try and post a message for now, see if we need to fix this?
@routes.route('/postMessage/<event_id>', methods=['POST'])
def post_message(event_id):
    #TODO if for some reason, we can't get certain form data, redirect to a failure page or put an alert on screen or something
    form_data = request.form.to_dict()
    #using the form data, create a new message object. this is fine because we have the ORM mapping
    new_message = Message(event_id=event_id,
                           display_name=form_data["display_name"],
                           message_content=form_data["message_content"])
    #add the new message to our database
    db.session.add(new_message)
    #commit it to the database
    db.session.commit()
    #TODO fix to redirect to event page, redirect back to share page for now
    return redirect(f'/share/{event_id}')

#routes that execute some simple database queries to fetch data
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
    #uses the model ORM to fetch all the messages from the database
    #equivalent to SELECT * FROM messages
    messages = db.session.query(Message).all()
    message_list = "\n".join(f"{msg.display_name} says: {msg.message_content}" for msg in messages)
    return Response(message_list, mimetype="text/plain")
