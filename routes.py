#file defines the routes for the application
import flask_login
from flask import send_file, abort, current_app, Blueprint, render_template, request, redirect, url_for, abort, flash
from flask_login import *
from sqlalchemy import desc
from models import User, Guestbook, Message
from extensions import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from icalendar import Calendar, Event
from datetime import datetime, timedelta, timezone
from io import BytesIO

#declare a blueprint hto hold all of our defined routes, expose templates folder
routes = Blueprint('routes', __name__, template_folder='templates')

#--------------- USER/SESSION MANAGEMENT------------------------ 
@routes.route('/')
@login_required
def index():
    user_guestbooks = None
    #if user is logged in, create some containers at the bottom of the page to represent existing guestbooks
    if current_user.is_authenticated:
        current_user_id = User.get_id(current_user)
        user_guestbooks = Guestbook.query.filter(Guestbook.owner_id==current_user_id).order_by(Guestbook.event_date).all()
        now = datetime.now()

        upcoming_events = [g for g in user_guestbooks if g.event_date >= now]
        past_events = [g for g in user_guestbooks if g.event_date < now]

        return render_template(
            'index.html',
            upcoming_events=upcoming_events,
            past_events=past_events,
            now=now
        )
    flash('Welcome! Please create your account to get started!', 'success')
    return redirect('/signup')

#handle new user signups
@routes.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')
@routes.route('/signup', methods=['POST'])
def handle_signup():
    #only want to create user when accessed via POST request
    if request.method == 'POST':
        #retrieve form data
        form_data = request.form.to_dict()
        
        #check if there is already a user in the database with that email. 
        duplicate_user = User.query.filter(User.email==form_data['email']).first()

        #if there's already a user with this email so, reject signup attempt
        if duplicate_user:
            flash('User already exists with current email.', category='error')
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
        flash("Account was successfully created!", category="success")
        return redirect('/login')

#handle user logins 
@routes.route('/login', methods=['GET'])
def login():
    return render_template('signin.html')
@routes.route('/login', methods=['POST'])
def login_user():
    if request.method == 'POST':
        #retrieve login details from form
        form_data = request.form.to_dict()

        #search the database for the account associated with that email
        login_attempt_user = User.query.filter(User.email==form_data['email']).first()

        #if no user exists for the email provided, reject login attempt
        if login_attempt_user is None:
            flash('No user exists with provided email.', category='error')
            return redirect('/login')

        #if a user does exist, validate their password 
        if check_password_hash(password=form_data['password'], pwhash=login_attempt_user.password_hash):
            # login and validate the user in the login manager
            flask_login.login_user(login_attempt_user)
            #if the user was successfully logged in, display a success message
            flash("Successfully logged in!", category='success')
            return redirect('/')
        # display alert on failed password
        else:
            flash('Incorrect password. Try again', category='error')
            return redirect('/login')

#allow user to logout
@routes.route('/logout')
@login_required
def logout():
    #logout using login manager
    logout_user()
    flash("Successfully logged out.", category='success')
    #redirect to home page on logout
    return redirect('/login') 

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
    
        #transform separate data/time entries into DATETIME data type
        datetime_format = '%Y-%m-%d %H:%M'
        event_datetime = datetime.strptime(f"{form_data['event_date']} {form_data['event_time']}", datetime_format)

        #using the form details and user's account data, create a new guestbook associated with the user
        #get the id from user that is currently logged in.
        new_guestbook = Guestbook(owner_id=User.get_id(current_user), event_date=event_datetime, 
                                  event_title=form_data['event_title'], event_address=form_data['event_address'])

        #stage the new guestbook for committment into the database
        db.session.add(new_guestbook)

        #try to commit the new guestbook to the database
        try:
            db.session.commit()
        #if an error occurs while trying to commit the new guestbook, raise an error
        except Exception as e:
            db.session.rollback()
            db.session.flush() 
            abort(400)
            
        #redirect to newly created event
        return redirect(f'/share/{new_guestbook.event_id}')

#render a custom share page for the event. restrict view to owner
@routes.route('/share/<event_id>')
@login_required 
def share_event(event_id):
    #first query the event details
    event_data = db.session.query(Guestbook).get(event_id)
    #if the event doesn't exist, throw a 404 error
    if event_data is None:
        abort(404)
    #if the person is not the owner, do not let them share the event
    if(User.get_id(current_user) != event_data.owner_id):
        return login_manager.unauthorized()
    return render_template('shareEvent.html', data=event_data)

#allow guestbook owner to edit existing event pages. must be logged in as the owner to view
@routes.route('/edit/<event_id>', methods=['GET'])
@login_required
def edit_event(event_id):
    #first query to see if the event exists
    event_data = db.session.query(Guestbook).get(event_id)
    #if the event doesn't exist, throw a 404 error
    if event_data is None:
        abort(404)
    #if the user id of the person doesn't match the person editing the event, throw an error
    if(User.get_id(current_user) != event_data.owner_id):
        return login_manager.unauthorized()
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

        #check if they are missing the time or date when trying to edit the start time
        if (('event_date' in updated_fields and form_data['event_date'] != '') and ('event_time' not in updated_fields or form_data['event_time'] == '')) \
         or (('event_time' in updated_fields and form_data['event_time'] != '') and ('event_date' not in updated_fields or form_data['event_date'] == '')):
            flash('You are missing either the time or date. Please try again.', category='error')
            return redirect(f"/edit/{event_id}")
        
        #format datetime and add to dictionary if time was updated
        if ('event_date' in updated_fields and form_data['event_date'] != '') and \
        ('event_time' in updated_fields and form_data['event_time'] != ''):
            datetime_format = '%Y-%m-%d %H:%M'
            form_data['event_date'] = datetime.strptime(f"{form_data['event_date']} {form_data['event_time']}", datetime_format)
        
        #remove the keys from the dictionary to prevent  errors when updating attributes
        if 'event_time' in updated_fields:
            form_data.pop('event_time')

        #update existing event details
        changed = False
        for key in updated_fields:
            if form_data[key] != '' and form_data[key] is not None:
                print(f"updated {form_data[key]}")
                setattr(guestbook, key, form_data[key])
                changed=True
        
        #commit to db only if object has been updated
        db.session.commit()
    #redirect back to event page
    flash("Event was successfully updated!", category='success')
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
    print(current_user.user_id)
    #if the event exists but there are no messages, encourage user to share their event            
    return render_template('event.html', event_data=event_data, messages_data=messages_data)

@routes.route('/delete/<event_id>', methods=['GET'])
@login_required
def delete_event(event_id):
    #get all of the event details based on event id
    event_data = db.session.query(Guestbook).get(event_id)
    #check to make sure that the event exists
    if event_data is None:
        abort(400)
    #make sure that the current user is the owner of the guestbook
    if(User.get_id(current_user) != event_data.owner_id):
        return login_manager.unauthorized()
    return render_template('deleteEvent.html', event_id=event_id)
@routes.route('/delete/<event_id>', methods=['POST'])
def handle_delete_event(event_id):
    #delete the event using the event id
    event_to_delete = Guestbook.query.filter(Guestbook.event_id==event_id).one()
    #commit changes to database instance
    db.session.delete(event_to_delete)
    db.session.commit()

    flash("Event was deleted successfully.", category='success')
    return redirect("/")

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

# ADD TO CALENDAR
@routes.route("/event/<event_id>/invite.ics", methods=["GET"])
def download_invite(event_id):
    # Using a universal .ics file so that the calendar invite can be opened on any device
    event = db.session.query(Guestbook).get(event_id)
    if event is None:
        abort(404)

    # iCalendar object is now instantiated
    cal = Calendar()
    cal.add("prodid", "-//Guestbook//EN")
    cal.add("version", "2.0")

    cal_event = Event()
    cal_event.add("uid", f"guestbook-{event.event_id}@example.com")
    cal_event.add("summary", event.event_title)

    # Will utilize the stored datetime; as a fallback, 2-hour duration will be used
    start = event.event_date
    end = start + timedelta(hours=2)
    cal_event.add("dtstart", start)
    cal_event.add("dtend", end)
    cal_event.add("dtstamp", datetime.now(timezone.utc))

    if event.event_address:
        cal_event.add("location", event.event_address)
    cal_event.add("description", "Created with Guestbook!")

    cal.add_component(cal_event)
    ics_bytes = cal.to_ical()

    buf = BytesIO(ics_bytes)
    buf.seek(0)
    filename = f"{event.event_title.replace(' ', '_')}-{start.date()}.ics"
    return send_file(buf, as_attachment=True, download_name=filename, mimetype="text/calendar")

#handles message deletion for guestbook owners
@routes.route('/deleteMessage/<msg_id>', methods=['GET'])
@login_required
def delete_message(msg_id):
    #get the message data using its ID
    message_to_delete = Message.query.filter(Message.msg_id==msg_id).first()
    #check to make sure the message exists
    if not message_to_delete:
        abort(404)
    # check to make sure the user deleting the message is the owner
    event_owner_id = message_to_delete.event.owner_id
    # Check permission before deleting
    if current_user.user_id != event_owner_id:
        return login_manager.unauthorized()
    return render_template('deleteMessage.html', msg_id=msg_id)
@routes.route('/deleteMessage/<msg_id>', methods=['POST'])
def handle_delete_message(msg_id):
    #delete the message using its ID
    message_to_delete = Message.query.filter(Message.msg_id==msg_id).one()
    #get the event id for rerouting
    event_id = message_to_delete.event_id
    #commit changes to database instance
    db.session.delete(message_to_delete)
    db.session.commit()

    flash("Message was successfully deleted.", category="success")
    return redirect(f"/event/{event_id}")

#---------------PREDEFINED TEMPLATES------------------------
#templates help guide users on the information to put in by providing "fill in the blank"-style forms
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
@routes.route('/createStPatty')
@login_required
def createStPatty():
    return render_template('createStPatty.html')

#--------------- ERROR HANDLING ------------------------
#404: page not founde
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
    flash('Sorry. you\'re not authorized to do that. Sign in or switch accounts.', category='error')
    return redirect('/login')
