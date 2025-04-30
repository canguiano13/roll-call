from flask import Blueprint, render_template, request, redirect, flash, abort, send_file
from flask_login import login_required, current_user
from sqlalchemy import desc
from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event
from io import BytesIO

from models import Guestbook, User, Message
from extensions import db, login_manager


events_bp = Blueprint('events', __name__)

# Create Event
@events_bp.route('/createevent', methods=['GET'])
@login_required
def create_event():
    return render_template('createEvent.html')


@events_bp.route('/createevent', methods=['POST'])
def handle_create_event():
    form_data = request.form.to_dict()
    datetime_format = '%Y-%m-%d %H:%M'
    event_datetime = datetime.strptime(f"{form_data['event_date']} {form_data['event_time']}", datetime_format)
    
    new_guestbook = Guestbook(
        owner_id=User.get_id(current_user),
        event_date=event_datetime,
        event_title=form_data['event_title'],
        event_address=form_data['event_address']
    )

    db.session.add(new_guestbook)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        db.session.flush()
        abort(400)

    return redirect(f'/share/{new_guestbook.event_id}')


# Share Event
@events_bp.route('/share/<event_id>')
@login_required
def share_event(event_id):
    event_data = Guestbook.query.get(event_id)
    if event_data is None:
        abort(404)
    if User.get_id(current_user) != event_data.owner_id:
        return login_manager.unauthorized()
    return render_template('shareEvent.html', data=event_data)


# Edit Event
@events_bp.route('/edit/<event_id>', methods=['GET'])
@login_required
def edit_event(event_id):
    event_data = Guestbook.query.get(event_id)
    if event_data is None:
        abort(404)
    if User.get_id(current_user) != event_data.owner_id:
        return login_manager.unauthorized()
    return render_template('editEvent.html', event_info={'event_id': event_id})


@events_bp.route('/edit/<event_id>', methods=['POST'])
def edit_event_details(event_id):
    form_data = request.form.to_dict()
    guestbook = Guestbook.query.get(event_id)
    if guestbook is None:
        abort(404)

    updated_fields = form_data.keys()

    if (('event_date' in updated_fields and form_data['event_date']) and ('event_time' not in updated_fields or not form_data['event_time'])) or \
       (('event_time' in updated_fields and form_data['event_time']) and ('event_date' not in updated_fields or not form_data['event_date'])):
        flash('You are missing either the time or date. Please try again.', 'error')
        return redirect(f"/edit/{event_id}")

    if form_data.get('event_date') and form_data.get('event_time'):
        datetime_format = '%Y-%m-%d %H:%M'
        form_data['event_date'] = datetime.strptime(f"{form_data['event_date']} {form_data['event_time']}", datetime_format)

    form_data.pop('event_time', None)

    for key in updated_fields:
        if form_data[key]:
            setattr(guestbook, key, form_data[key])

    db.session.commit()
    flash("Event was successfully updated!", 'success')
    return redirect(f"/event/{event_id}")


# View Event Page
@events_bp.route('/event/<event_id>', methods=['GET'])
def render_event_page(event_id):
    event_data = Guestbook.query.get(event_id)
    messages_data = Message.query.filter_by(event_id=event_id).order_by(desc(Message.msg_id)).all()
    if event_data is None:
        abort(404)
    return render_template('event.html', event_data=event_data, messages_data=messages_data)


# Delete Event
@events_bp.route('/delete/<event_id>', methods=['GET'])
@login_required
def delete_event(event_id):
    event_data = Guestbook.query.get(event_id)
    if event_data is None:
        abort(400)
    if User.get_id(current_user) != event_data.owner_id:
        return login_manager.unauthorized()
    return render_template('deleteEvent.html', event_id=event_id)


@events_bp.route('/delete/<event_id>', methods=['POST'])
def handle_delete_event(event_id):
    event_to_delete = Guestbook.query.filter_by(event_id=event_id).one()
    db.session.delete(event_to_delete)
    db.session.commit()
    flash("Event was deleted successfully.", 'success')
    return redirect("/")


# Download Calendar Invite (.ics)
@events_bp.route("/event/<event_id>/invite.ics", methods=["GET"])
def download_invite(event_id):
    event = Guestbook.query.get(event_id)
    if event is None:
        abort(404)

    cal = Calendar()
    cal.add("prodid", "-//Guestbook//EN")
    cal.add("version", "2.0")

    cal_event = Event()
    cal_event.add("uid", f"guestbook-{event.event_id}@example.com")
    cal_event.add("summary", event.event_title)
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
