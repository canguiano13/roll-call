from extensions import db


#mirror guestbooks database
class Guestbook(db.Model):
    __tablename__ = 'guestbooks'

    event_id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id        = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    event_date      = db.Column(db.DateTime, nullable=False)
    event_title     = db.Column(db.Text, nullable=False)
    event_address   = db.Column(db.Text, nullable=False)
    event_img       = db.Column(db.Text)

    #define a relationship with the messages table
    messages = db.relationship('Message', backref='event', lazy=True)

    def __repr__(self):
        return f'<GUESTBOOK {self.event_id}: {self.event_title}@{self.event_address} STARTING {self.event_date}>'