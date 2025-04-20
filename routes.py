#file defines the routes for the application
import flask_login
from flask import Blueprint, Response, render_template, request, redirect, url_for, abort, flash
from sqlalchemy import desc
from flask_login import *
from models import User, Guestbook, Message
from extensions import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

#declare a blueprint hto hold all of our defined routes, expose templates folder
routes = Blueprint('routes', __name__, template_folder='templates')

#--------------- USER/SESSION MANAGEMENT------------------------ 
@routes.route('/')
def index():
    #TODO if user is logged in, create some containers at the bottom of the page to represent existing guestbooks
    #if current_user.is_authenticated:
        #user_guestbooks = db.session.query()
    return render_template('index.html', guestbooks_data=None) #TODO fix this None to hold the user's guestbooks

#handle new user signups
@routes.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')
@routes.route('/signup', methods=['POST'])
def handle_signup():
    #only want to create user when accessed via POST request
    if request.method == "POST":
        #retrieve form data
        form_data = request.form.to_dict()
        
        #check if there is already a user in the database with that email. 
        duplicate_user = User.query.filter(User.email==form_data['email']).first()

        #if there's already a user with this email so, reject signup attempt
        if duplicate_user:
            flash('User already exists with current email.')
            return redirect('/signup')

        #hash the password so it is not stored in plaintext
        #werkzeug has a built-in hash password function! no external libs needed :)
        hashed_password = generate_password_hash(password=form_data['password_hash'])
        
        #instantiate new user using DB model
        new_user = User(first_name=form_data['first_name'], last_name=form_data['last_name'], 
                        email=form_data['email'], password_hash=hashed_password)
        
        #add and commit new user to database
        db.session.add(new_user)
        db.session.commit()
        
        #route user back to home page, this time will display any guestbooks
        return redirect('/')

#handle user logins 
@routes.route('/login', methods=['GET'])
def login():
    return render_template('signin.html')
@routes.route('/login', methods=['POST'])
def login_user():
    if request.method == "POST":
        #retrieve login details from form
        form_data = request.form.to_dict()

        #search the database for the account associated with that email
        login_attempt_user = User.query.filter(User.email==form_data['email']).first()

        #if no user exists for the email provided, reject login attempt
        if login_attempt_user is None:
            flash('No user exists with provided email.')
            return redirect('/login')

        #if a user does exist, validate their password 
        if check_password_hash(password=form_data['password'], pwhash=login_attempt_user.password_hash):
            # login and validate the user in the login manager.
            flask_login.login_user(login_attempt_user)
            return redirect('/')
        # display alert on failed password
        else:
            flash('Incorrect password. Try again')
            return redirect('/login')

#allow user to logout
@routes.route("/logout")
@login_required
def logout():
    logout_user()
    #redirect to home page on logout
    return redirect('/') 

#----------------EVENT/MESSAGE MANAGEMENT------------------------
#handle creation of new guestbooks
@routes.route('/createevent', methods=['GET'])
@login_required
def create_event():
    #if the user tries to create an event while not signed in, reroute to sign-in page
    return render_template('createEvent.html')
@routes.route('/createevent', methods=['POST']) 
def handle_create_event():
    if request.method == 'POST':
        #retrieve form data
        form_data = request.form.to_dict()
        
        event_details=f'''
            NEW EVENT REQUEST... \n
            event_title:        {form_data['event_title']}\n
            event_description:  {form_data['event_address']}\n
            event_datetime:     {form_data['event_date']} \n 
            event_time:         {form_data['event_time']} \n
            '''
    
        #transform separate data/time entries into DATETIME data type
        datetime_format = '%Y-%m-%d %H:%M'
        event_datetime = datetime.strptime(f"{form_data['event_date']} {form_data['event_time']}", datetime_format)

        #using the form details and user's account data, create a new guestbook associated with the user
        new_guestbook = Guestbook(owner_id=login_manager.user_loader, event_date=event_datetime, event_title=form_data['event_title'], event_address=form_data['event_address'])

        #add and commit the new guestbook to our database
        db.session.add(new_guestbook)
        db.session.commit()

        #redirect to newly created event
        return redirect(f'/share/{new_guestbook.event_id}')

#allow guestbook owner to edit existing event pages. must be logged in as the owner to view
#TODO abort to unauthorization error if trying to edit as non-owner
@routes.route('/edit/<event_id>', methods=["GET"])
@login_required
def edit_event(event_id):
    #will need to get all of the event details based on event id
    return render_template('editEvent.html', event_info={'event_id':event_id})
@routes.route('/edit/<event_id>', methods=['POST'])
def edit_event_details(event_id):
    if request.method == 'POST':
        #fetch form data
        form_data = request.form.to_dict()
        #fetch corresponding event from database
        guestbook = db.session.query(Guestbook).get(event_id)
        #if no guestbook is found, route to error page
        if guestbook is None:
            abort(404)

        #get the keys for the data that was updated
        updated_fields = form_data.keys()
        #format datetime and add to dictionary if time was updated
        if ('event_date' in updated_fields and form_data['event_date'] != '') and \
        ('event_time' in updated_fields and form_data['event_time'] != ''):
            datetime_format = '%Y-%m-%d %H:%M'
            form_data['event_datetime'] = datetime.strptime(f"{form_data['event_date']} {form_data['event_time']}", datetime_format)
        #remove the keys from the dictionary to prevent  errors when updating attributes
        if 'event_date' in updated_fields:
            form_data.pop('event_date')
        if 'event_time' in updated_fields:
            form_data.pop('event_time')

        #update existing event details
        changed = False
        for key in updated_fields:
            if form_data[key] != '' and form_data[key] is not None:
                setattr(guestbook, key, form_data[key])
                changed=True
        
        #commit to db only if object has been updated
        if changed:
            try:
                db.session.commit()
            #if an error occurs while trying to commit the updated guestbook, raise an error
            except Exception as e:
                db.session.rollback()
                db.session.flush() 
                abort(400)

    #redirect back to event page
    return redirect(f'/event/{event_id}')

#anyone can view/post messages to a guestbook page
@routes.route('/event/<event_id>', methods=['GET'])
def render_event_page(event_id):
    #get all of the event details based on event id
    event_data = db.session.query(Guestbook).get(event_id)
    #get the list of messages for the event, then put them in order from most to least recent
    messages_data = db.session.query(Message).filter(Message.event_id==event_id).order_by(desc(Message.msg_id)).all()
    #if the event doesn't exist, redirect to a 404
    if event_data is None:
        abort(404)
    #if the event exists but there are no messages, encourage user to share their event            
    return render_template('event.html', event_data=event_data, messages_data=messages_data)

#populate the database with incoming messages for a specific event page
@routes.route('/postMessage/<event_id>', methods=['POST'])
def post_message(event_id):
    #fetch form data
    form_data = request.form.to_dict()

    #ensure that the guestbook that the message is being posted to exists
    guestbook = db.session.query(Guestbook).get(event_id)
    #if no guestbook is found, route to error page
    if guestbook is None:
        abort(404)

    #using the form data, create a new message object. this works because we have the ORM mapping
    new_message = Message(event_id=event_id, display_name=form_data['display_name'], message_content=form_data['message_content'])
    #add the new message to our database
    db.session.add(new_message)
    
    try:
        db.session.commit()
    #if an error occurs while trying to commit the updated guestbook, raise an error
    except Exception as e:
        db.session.rollback()
        db.session.flush() 
        abort(400)
    #redirect back to event page which will display new message
    return redirect(f'/event/{event_id}')

#---------------PREDEFINED TEMPLATES------------------------
#templates help guide users on the information to put in
#login is required for any template as this is just another version of the create_event form
#birthday template
@routes.route('/createBirthday')
@login_required
def createBirthday():
    return render_template('createBirthday.html')
#christmas template
@routes.route('/createChristmas')
@login_required
def createChristmas():
    return render_template('createChristmas.html')
#halloween template can route here
@routes.route('/createHalloween')
@login_required
def createHalloween():
    return render_template('createHalloween.html')
#st. patrick's day template can route here
#TODO create template and outline logic
@routes.route('/createStPatty')
@login_required
def createStPatty():
    return render_template('createStPatty.html')

#--------------- ERROR HANDLING ------------------------
#404: page not found
@routes.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

#400: bad request
@routes.errorhandler(400)
def page_not_found(error):
    return render_template('400.html'), 400

#401: user is not authorized due to not logging in
@login_manager.unauthorized_handler
def unauthorized():
    # add a flash message to the sign in page while redirecting
    flash("Sorry,you're not authorized to do that. Sign in or switch accounts.")
    return redirect('/login')
