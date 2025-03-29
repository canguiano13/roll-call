# mirrors the messages database for easier writing/reading
from extensions import db

class Message(db.Model):
    __tablename__ = 'messages'

    msg_id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id        = db.Column(db.Integer, db.ForeignKey('guestbooks.event_id', ondelete="CASCADE"), nullable=False)
    display_name    = db.Column(db.Text, nullable=False)
    message_content = db.Column(db.Text, nullable=False)

    #defines the representation for logging
    def __repr__(self):
        return f"<Message from {self.display_name}>"
