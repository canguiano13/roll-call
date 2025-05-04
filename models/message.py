from extensions import db


#mirror messages database
class Message(db.Model):
    __tablename__ = 'messages'

    msg_id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id        = db.Column(db.Integer, db.ForeignKey('guestbooks.event_id', ondelete='CASCADE'), nullable=False)
    display_name    = db.Column(db.Text, nullable=False)
    message_content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Message from {self.display_name}>'