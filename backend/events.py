from flask import Blueprint, render_template, request, redirect, flash, abort, send_file
from flask_login import login_required, current_user
from sqlalchemy import desc
from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event
from io import BytesIO

from models import Guestbook, User, Message
from extensions import db, login_manager


events = Blueprint('events', __name__)

#handles creation of new event
@events.route('/createevent', methods=['GET', 'POST'])
@login_required
def handle_create_event():
    #render frontend template for GET requests
    if request.method == 'GET':
        return render_template('createEvent.html')
    
    elif request.method == 'POST':    #retrieve form data
        form_data = request.form.to_dict()

        #combine separate date/time fields into single datetime type
        datetime_format = '%Y-%m-%d %H:%M'
        event_datetime = datetime.strptime(f"{form_data['event_date']} {form_data['event_time']}", datetime_format)
        
        #instantiate new guestbook using form data
        new_guestbook = Guestbook(
            owner_id=User.get_id(current_user),
            event_date=event_datetime,
            event_title=form_data['event_title'],
            event_address=form_data['event_address']
        )

        #commit new guestbook to database
        db.session.add(new_guestbook)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            db.session.flush()
            abort(500)

        return redirect(f'/share/{new_guestbook.event_id}')

#renders custom share page for each event
@events.route('/share/<event_id>')
@login_required
def share_event(event_id):
    #get the event data using its ID
    event_data = Guestbook.query.get(event_id)

    #validate existence of guestbook
    if event_data is None:
        abort(404)
    #only allow the owner of the guestbook to see the share page
    if User.get_id(current_user) != event_data.owner_id:
        abort(403)
    
    return render_template('shareEvent.html', data=event_data)

#handles editing of existing event's details
@events.route('/edit/<event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    #get the event details using the ID
    guestbook = Guestbook.query.get(event_id)

    #validate existence of event
    if not guestbook:
        abort(404)
    #only allow owner of guestbook to edit event details
    if User.get_id(current_user) != guestbook.owner_id:
        abort(403)
    
    #render frontend template for GET request
    if request.method == 'GET':
        return render_template('editEvent.html', event_id=event_id)
    elif request.method == 'POST':
        form_data = request.form.to_dict()
        #get list of attributes the owner is attempting to update
        updated_fields = form_data.keys()

        #do not allow the owner to edit only the date or time
        if (('event_date' in updated_fields and form_data['event_date']) and ('event_time' not in updated_fields or not form_data['event_time'])) or \
        (('event_time' in updated_fields and form_data['event_time']) and ('event_date' not in updated_fields or not form_data['event_date'])):
            flash('Must edit either both or neither the date/time. Please try again.', 'error')
            return redirect(f"/edit/{event_id}")
        
        #combine separate date/time fields if both are provided
        if form_data.get('event_date') and form_data.get('event_time'):
            datetime_format = '%Y-%m-%d %H:%M'
            form_data['event_date'] = datetime.strptime(f"{form_data['event_date']} {form_data['event_time']}", datetime_format)
        form_data.pop('event_time', None)

        #update event attributes using ORM models
        for key in updated_fields:
            if form_data[key]:
                setattr(guestbook, key, form_data[key])

        #push updates to database
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            db.session.flush()
            abort(500)

        #display success message on next page
        flash("Event was successfully updated!", 'success')
        return redirect(f"/event/{event_id}")

#render event details and posted messages for individual event
@events.route('/event/<event_id>', methods=['GET'])
def render_event(event_id):
    #get event details
    event_data = Guestbook.query.get(event_id)
    #validate existence of guestbook
    if not event_data:
        abort(404)
    #get all messages posted on the event page
    #put most recently posted messages at the top
    messages_data = Message.query.filter_by(event_id=event_id).order_by(desc(Message.msg_id)).all()
    #render custom event page
    return render_template('event.html', event_data=event_data, messages_data=messages_data)

#handles deletion of existing events
@events.route('/delete/<event_id>', methods=['GET', 'POST'])
def handle_delete_event(event_id):
    #get event details using its ID
    event_to_delete = Guestbook.query.get(event_id)
    #validate existence of event
    if not event_to_delete:
        abort(404)
    if User.get_id(current_user) != event_to_delete.owner_id:
        abort(403)

    #render frontend confirmation page for GET request
    if request.method == 'GET':
        return render_template('deleteEvent.html', event_id=event_id)
    #perform deletion once confirmed
    elif request.method == 'POST':
        #delete event
        db.session.delete(event_to_delete)
        #propagate updates to database
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            db.session.flush()
            abort(500)
        #display success message on next page
        flash("Event was deleted successfully.", 'success')
        return redirect("/")

# download Calendar Invite (.ics)
@events.route("/event/<event_id>/invite.ics", methods=["GET"])
def download_invite(event_id):
    #get event details
    event = Guestbook.query.get(event_id)
    #validate existence of event
    if event is None:
        abort(404)

    #instantiate iCalendar object
    cal = Calendar()
    cal.add("prodid", "-//Guestbook//EN")
    cal.add("version", "2.0")

    #add event details
    cal_event = Event()
    cal_event.add("uid", f"guestbook-{event.event_id}@example.com")
    cal_event.add("summary", event.event_title)
    
    # utilize the stored datetime; as a fallback, 2-hour duration will be used
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


#templates help guide users on the information to put in by providing "fill in the blank"-style forms
#login is required for any template as this is just another version of the create_event form
@events.route('/createBirthday')
@login_required
def create_birthday():
    return render_template('createBirthday.html')

@events.route('/createChristmas')
@login_required
def create_christmas():
    return render_template('createChristmas.html')

@events.route('/createHalloween')
@login_required
def create_halloween():
    return render_template('createHalloween.html')

@events.route('/createStPatty')
@login_required
def create_stpatty():
    return render_template('createStPatty.html')