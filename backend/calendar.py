from flask import Blueprint, send_file, abort
from datetime import datetime, timedelta, timezone
from io import BytesIO
from icalendar import Calendar, Event

from models import Guestbook

calendar_bp = Blueprint('calendar', __name__)

# Export a calendar invite for the event
@calendar_bp.route("/event/<event_id>/invite.ics", methods=["GET"])
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
