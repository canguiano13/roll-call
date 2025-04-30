from flask import Blueprint, render_template, request, redirect, flash, abort
from flask_login import login_required, current_user

from models import Message
from extensions import db, login_manager

messages_bp = Blueprint('messages', __name__)

# Post a message to an event
@messages_bp.route('/postMessage/<event_id>', methods=['POST'])
def post_message(event_id):
    form_data = request.form.to_dict()

    guestbook = db.session.query(Message.event.property.mapper.class_).get(event_id)
    if guestbook is None:
        abort(404)

    new_message = Message(
        event_id=event_id,
        display_name=form_data['display_name'],
        message_content=form_data['message_content']
    )
    db.session.add(new_message)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        db.session.flush()
        abort(400)

    return redirect(f'/event/{event_id}')


# Delete a message (GET confirmation)
@messages_bp.route('/deleteMessage/<msg_id>', methods=['GET'])
@login_required
def delete_message(msg_id):
    message_to_delete = Message.query.filter_by(msg_id=msg_id).first()
    if not message_to_delete:
        abort(404)

    event_owner_id = message_to_delete.event.owner_id
    if current_user.user_id != event_owner_id:
        return login_manager.unauthorized()

    return render_template('deleteMessage.html', msg_id=msg_id)


# Delete a message (POST confirmed)
@messages_bp.route('/deleteMessage/<msg_id>', methods=['POST'])
def handle_delete_message(msg_id):
    message_to_delete = Message.query.filter_by(msg_id=msg_id).one()
    event_id = message_to_delete.event_id

    db.session.delete(message_to_delete)
    db.session.commit()

    flash("Message was successfully deleted.", category="success")
    return redirect(f"/event/{event_id}")
