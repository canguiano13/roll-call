#file defines the routes for the application
from flask import Blueprint, Response, render_template, request, redirect, url_for, abort
from sqlalchemy import desc
from flask_login import current_user, login_required
from models import User, Guestbook, Message
from extensions import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

#declare a blueprint hto hold all of our defined routes, expose templates folder
routes = Blueprint('routes', __name__, template_folder='templates')

#declare user loader for login manager
@login_manager.user_loader
def load_user(user_id):
    #some things we can do with the login manager
    #check if they are authenticated
    print(f"***********\n\n")
    print(f"AUTHENTICATED? {current_user}")
    print(f"USER ID IS {user_id}\n***********")
    print()
    return User.get(user_id) #uses the database model to pull the id of a specified user

#TODO fix routes to be in all lowercase, probably better ux
@routes.route('/')
def index():
    #TODO if user is logged in, create some divs to represent existing guestbooks
    return render_template('index.html')

#--------------- USER/SESSION MANAGEMENT------------------------
#handles new user signups
@routes.route('/signUp')
def signup():
    #check if any alert data was passed due to failed signup attempt
    return render_template('signup.html', alert_data=request.args.get('alert_data'))
@routes.route('/handleSignUp', methods=["POST"])
def handle_signup():
    #only want to create user when accessed via POST request
    if request.method == "POST":
        #retrieve form data
        form_data = request.form.to_dict()
        
        #check if there is already a user in the database with that email. If so, reject signup attempt
        duplicate_user = db.session.execute(db.select(User).filter_by(email=form_data['email'])).scalar_one_or_none()
        if duplicate_user:
            return redirect(url_for("routes.signup", alert_data='User already exists with provided email.'))

        #hash the password so it is not stored in plaintext
        #werkzeug has a built-in hash password function! no external libs needed :)
        #TODO research if we can use flask user management library somewhere in here
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
@routes.route('/signIn')
def signin():
    #check if any alert data was passed due to failed login attempt
    return render_template('signin.html', alert_data=request.args.get('alert_data'))
@routes.route('/handleSignIn', methods=['POST'])
def login_user():
    if request.method == "POST":
        #retrieve login details from form
        form_data = request.form.to_dict()

        #search the database for the account associated with that email
        login_attempt_user = db.session.execute(db.select(User).filter_by(email=form_data['email'])).scalar_one_or_none()

        #if no user exists for the email provided, reject login attempt
        #need to use redirect with url_for to provide alert data
        if login_attempt_user is None:
            return redirect(url_for("routes.signin", alert_data='No user exists with provided email.'))

        #if a user does exist, validate their password and send them to home page if successful
        if check_password_hash(password=form_data['password'], pwhash=login_attempt_user.password_hash):
            return redirect('/')
        else:
            return redirect(url_for("routes.signin", alert_data='Incorrect password. Try again.'))


#----------------EVENT/MESSAGE MANAGEMENT------------------------
#handle creation of new guestbooks
@routes.route('/createEvent')
def create_event():
    return render_template('createEvent.html')
@routes.route('/handleCreateEvent', methods=['POST']) 
def handle_new_event():
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
        new_guestbook = Guestbook(owner_id=current_user.id, event_date=event_datetime, event_title=form_data['event_title'], event_address=form_data['event_address'])

        #add and commit the new guestbook to our database
        db.session.add(new_guestbook)
        db.session.commit()

        #redirect to newly created event
        return redirect(f'/share/{new_guestbook.event_id}')

#allow guestbook owner to edit existing event pages
@routes.route('/edit/<event_id>')
def edit_event(event_id):
    #will need to get all of the event details based on event id
    return render_template('editEvent.html', event_info={'event_id':event_id})
@routes.route('/handleEditEvent/<event_id>', methods=['POST'])
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
            db.session().commit()

    #redirect back to event page
    return redirect(f'/event/{event_id}')

#render a custom share page for the event
@routes.route('/share/<event_id>')
def share_event(event_id):#
    #first query the event details
    event_data = db.session.query(Guestbook).get(event_id)
    #if the event doesn't exist, throw a 404 error
    if event_data is None:
        abort(404)
    return render_template('shareEvent.html', data=event_data)

#TODO define html template for event page
@routes.route('/event/<event_id>', methods=['GET'])
def render_event_page(event_id):
    #get all of the event details based on event id
    event_data = db.session.query(Guestbook).get(event_id)
    #get the list of messages for the event, then put them in order from most to least recent
    messages_data= db.session.query(Message).filter(Message.event_id==event_id).order_by(desc(Message.msg_id)).all()
    #notice to display if there are no messages yet
    no_message_notice = dict()
    #if the event doesn't exist, redirect to a 404
    if event_data is None:
        abort(404)
    #if the event exists but there are no messages, encourage user to share their event            
    elif messages_data is None:
        no_message_notice['content'] = "Hmm...there aren't any messages."
    return render_template('event.html', event_data=event_data, messages_data=messages_data, no_message_notice=no_message_notice)

#populate the database with incoming messages for a specific event page
@routes.route('/postMessage/<event_id>', methods=['POST'])
def post_message(event_id):
    #TODO if for some reason, we can't get certain form data, redirect to a failure page or put an alert on screen or something
    form_data = request.form.to_dict()
    #using the form data, create a new message object. this works because we have the ORM mapping
    new_message = Message(event_id=event_id, display_name=form_data['display_name'], message_content=form_data['message_content'])
    #add the new message to our database
    db.session.add(new_message)
    #commit it to the database
    db.session.commit()
    #TODO fix to redirect to event page, redirect back to share page for now
    return redirect(f'/event/{event_id}')

#---------------PREDEFINED TEMPLATES------------------------
#birthday template can route here
#TODO create template and refine redirect logic
@routes.route('/createBirthday')
def createBirthday():
    return render_template('createBirthday.html')
#christmas template can route here
#TODO create template and refine redirect logic
@routes.route('/createChristmas')
def createChristmas():
    return render_template('createChristmas.html')
#halloween template can route here
#TODO create template and outline logic
@routes.route('/createHalloween')
def createHalloween():
    return render_template('createHalloween.html')
#st. patrick's day template can route here
#TODO create template and outline logic
@routes.route('/createStPatty')
def createStPatty():
    return render_template('createStPatty.html')

#--------------- ERROR HANDLING ------------------------
#404: page not found
@routes.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
