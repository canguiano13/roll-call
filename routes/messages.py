from flask import Blueprint, render_template, request, redirect, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models import User, Guestbook, Message


messages = Blueprint('messages', __name__)

# post new message to event page
@messages.route('/postMessage/<event_id>', methods=['POST'])
def post_message(event_id):
    #get guestbook using event ID
    guestbook = db.session.query(Guestbook).get(event_id)
    #validate existence of guestbook
    if guestbook is None:
        abort(404)
    #instantiate new message using form data
    form_data = request.form.to_dict()
    new_message = Message(
        event_id=event_id,
        display_name=form_data['display_name'],
        message_content=form_data['message_content']
    )
    #propagate update to database
    db.session.add(new_message)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        db.session.flush()
        abort(500)
    
    return redirect(f'/event/{event_id}')

# delete existing message on guestbook
@messages.route('/deleteMessage/<msg_id>', methods=['GET', 'POST'])
@login_required
def delete_message(msg_id):
    #get message details using ID
    message_to_delete = Message.query.filter_by(msg_id=msg_id).first()
    #validate existence of message
    if not message_to_delete:
        abort(404)
    #only allow the owner of the guestbook to delete messages
    event_owner_id = message_to_delete.event.owner_id
    if current_user.user_id != event_owner_id:
        abort(403)
    
    #confirm message deletion (GET)
    if request.method == 'GET':
        return render_template('deleteMessage.html', msg_id=msg_id)
    
    #delete message (POST confirmed)
    elif request.method == 'POST':
        #propagate updates to database
        db.session.delete(message_to_delete)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            db.session.flush()
            abort(500)
        #display success message
        flash("Message was successfully deleted.", category="success")
        return redirect(f"/event/{message_to_delete.event.event_id}")
