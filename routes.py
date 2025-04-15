#file defines the routes for the application
from flask import Blueprint, Response, render_template, request, redirect, url_for, abort
from models import User, Guestbook, Message
from db import db
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash

#declare a blueprint hto hold all of our defined routes, expose templates folder
routes = Blueprint('routes', __name__, template_folder='templates')

#TODO fix routes to be in all lowercase, probably better ux
@routes.route('/')
def index():
    return render_template('index.html')

#--------------- USER/SESSION MANAGEMENT------------------------
#TODO figure out if we can use flask login management library here
#handles new user signups
@routes.route('/signUp')
def signup():
    return render_template('signup.html')
@routes.route('/handleSignUp', methods=['POST'])
def create_user():
    #only want to create user when accessed via POST request
    if request.method == 'POST':
        #retrieve parameters here
        form_data = request.form.to_dict()
        
        #hash the password so it is not stored in plaintext
        #werkzeug has a built-in hash password function! no external libs needed :)
        #TODO research if we need to change method/salt_length
        #TODO research if we can use flask user management library somewhere in here
        hashed_password = generate_password_hash(password=form_data['password_hash'],
                                                 method='something',
                                                 salt_length='some-number')
        
        event_details=f'''
            NEW USER REQUEST. CREATING USER...\n
            first_name: {form_data['first_name']}\n
            last_name:  {form_data['last_name']}\n
            email:      {form_data['email']}\n
            password:   {form_data['password_hash']}\n
            '''
        #TODO figure out how to handle profile pics. they are optional
        #TODO figure out how to handle user trying to create an account with an email that already exists
        #new_user = User(first_name=form_data['first_name'], last_name=form_data['last_name'], 
        #               email=form_data['email'], password_hash=hashed_password, profile_pic=TODO)

        #add and commit the new user to our database
        #db.session.add(new_user)
        #db.session.commit()

        #TODO route to success page? or figure out another way to handle new user creation
    return Response(event_details, mimetype='text/plain')

#handle user logins 
#TODO figure out password resets?
@routes.route('/signIn')
def signin():
    return render_template('signin.html')
@routes.route('/handleSignIn', methods=['POST'])
def login_user():
    #only want to create user when accessed via POST request
    if request.method == 'POST':
        #retrieve parameters here
        form_data = request.form.to_dict()
        #query the database for the user with this email
        #if login succeeds, redirect user back to home page

        #TODO use werkzeug.security check_password_hash function
        
        #if check_password_hash(form_data['password_hash', db.session.query(..)]:
            #password succeeds
            
        #TODO if login fails, redirect back to sign-in page with failure message
        login_details =f'''
            USER IS LOGGING IN WITH DETAILS...\n
            email:                    {form_data['email']}\n
            password_hash (attempted) {form_data['password_hash']}\n
            '''
    return Response(login_details, mimetype='text/plain')

#----------------EVENT/MESSAGE MANAGEMENT------------------------
#render template for new event
@routes.route('/createEvent')
def create_event():#
    return render_template('createEvent.html')

#TODO fix method
#For handling request form data we can get the form inputs value by using POST attribute.
@routes.route('/handleCreateEvent', methods=['POST']) 
def handle_new_event():
    if request.method == 'POST':
        #retrieve parameters here
        form_data = request.form.to_dict()
        print(form_data)
        event_details=f'''
            NEW EVENT REQUEST... \n
            event_title:        {form_data['event_title']}\n
            event_description:  {form_data['event_address']}\n
            event_datetime:     {form_data['event_date']} \n 
            event_time:         {form_data['event_time']} \n
            '''
    
        #TODO Transform separate data/time entries into DATETIME data type
        #event_datetime=...

        #TODO need to figure out how we are sourcing the owner_id
        #TODO figure out how to handle the images, they are optional so some guestbooks will have them and others will not
        #using the form details and user's account data, create a new guestbook associated with the user
        #new_guestbook = Guestbook(owner_id=TODO, event_date=event_datetime, event_title=form_data['event_title'], 
        #                          event_address=form_data['event_address'], event_img=TODO)

        #add and commit the new guestbook to our database
        #db.session.add(new_guestbook)
        #db.session.commit()

        #return redirect(f'/share/{new_guestbook.event_id}')
        return redirect('/share/1')

#render a custom share page for the event
@routes.route('/share/<event_id>')
def share_event(event_id):
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
    #if the event doesn't exist, redirect to a 404
    if event_data is None:
        abort(404)
    #TODO define action when an event exists but there are no messages                     
    elif messages_data is None:
        print('no messages.')
    return render_template('event.html', event_data=event_data, messages_data=messages_data)

#this route will be used to populate the database with incoming messages for a specific event page
#TODO will need to pass the event id when we try and post a message for now, see if we need to fix this?
@routes.route('/handlePostMessage/<event_id>', methods=['POST'])
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
    return redirect(f'/allmessages')

#---------------PREDEFINED TEMPLATES------------------------
#birthday template can route here
#TODO create template and refine redirect logic
@routes.route('/birthdayTemplate')
def birthday_template():
    return 'happy birthday'
#christmas template can route here
#TODO create template and refine redirect logic
@routes.route('/christmasTemplate')
def christmas_template():
    return 'merry christmas'
#halloween template can route here
#TODO create template and outline logic
@routes.route('/halloweenTemplate')
def halloween_template():
    return 'happy halloween'
#st. patrick's day template can route here
#TODO create template and outline logic
@routes.route('/stPaddyTemplate')
def st_paddy_template():
    return 'happy st. paddy\'s day'

#--------------- ERROR HANDLING ------------------------
#404: page not found
@routes.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

#---------------#TODO can remove these later------------------------
#routes that execute some simple database queries to fetch data
#uses the model ORM to fetch all the messages from the database
#equivalent to 'SELECT * FROM' statements
@routes.route('/allusers', methods=['GET'])
def getallusers():
    users = db.session.query(User).all()
    user_list = '\n'.join(f'{user.first_name} {user.last_name}: {user.email}' for user in users)
    return Response(user_list, mimetype='text/plain')
@routes.route('/allguestbooks', methods=['GET'])
def getallguestbooks():
    guestbooks = db.session.query(Guestbook).all()
    guestbook_list = '\n'.join(f'EVENT {gb.event_title} ({gb.event_date}) happening at: {gb.event_address}' for gb in guestbooks)
    return Response(guestbook_list, mimetype='text/plain')
@routes.route('/allmessages', methods=['GET'])
def getallmessages():
    messages = db.session.query(Message).all()
    message_list = '\n'.join(f'{msg.display_name} says: {msg.message_content}' for msg in messages)
    return Response(message_list, mimetype='text/plain')
