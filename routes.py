#defines the routes for the application
from flask import Blueprint, Response, render_template, request
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
        #TODO hash password here
        #form_details['user-pass'] = hashpassword(form_details['user-pass'])
        event_details=f'''
            NEW USER REQUEST. CREATING USER...\n
            first-name: {form_details['first-name']}\n
            last-name:  {form_details['last-name']}\n
            email:      {form_details['user-email']}\n
            password:   {form_details['user-pass']}\n
            '''
        #call db.py function here? e.g.
        #create_user_in_table(firstname=XX, lastname=XX, email=XX, pass=hash(XX))
        
        #then route to success page?
    return Response(event_details, mimetype='text/plain')

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
        login_details =f'''
            USER IS LOGGING IN WITH DETAILS...\n
            user-email:          {form_details['user-email'] if form_details["user-email"] else None}\n
            user-pass (attempted) {form_details['user-pass'] if  form_details["user-pass"] else None}\n
            '''
    return Response(login_details, mimetype='text/plain')


#creating and handling new event
@routes.route('/createEvent')
def create_event():
    return render_template('createEvent.html')
#For handling request form data we can get the form inputs value by using POST attribute.
@routes.route('/handleCreateEvent', methods=["POST"]) 
def handle_new_event():
    #retrieve parameters here
    form_details = request.form.to_dict()
    event_details=f'''
        NEW EVENT REQUEST... \n
        event-title:        {form_details['event-title']}\n
        event-description:  {form_details['event-description']}\n
        event-date:         {form_details['event-date']} \n
        event-time:         {form_details['event-time']} \n
        '''
    return Response(event_details, mimetype='text/plain')

#TODO find a way to put the event id into here so that the correct link is generated for each event
@routes.route('/share/event-id')
def share_event():
    return render_template('shareEvent.html')

#some simple database queries   
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
