#import the SQLAlchemy db module
from db import db

## DEFINE DB MODELS FOR ORM (Object-Relational Mapping) CAPABILITIES.
#mirrors users database
class User(db.Model):
    #Flask-SQLAlchemy’s model will automatically generate a table name if __tablename__ is not set
    __tablename__ = 'users'

    user_id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password_hash   = db.Column(db.Text, nullable=False)
    first_name      = db.Column(db.Text, nullable=False)
    last_name       = db.Column(db.Text, nullable=False)
    email           = db.Column(db.String(255), unique=True, nullable=False)
    profile_pic     = db.Column(db.Text) #URL to profile photo?

    #defines a one-to-many relationship between users and guestbooks but does not affect the database schema. 
    #relationship provides a convenient way to access related objects. 
    #backref then adds a parent attribute to all Child objects (e.g guestbook.parent is the owner)
    guestbooks = db.relationship('Guestbook', backref='owner', cascade="all, delete-orphan")

    #defines the representation for User objects when printed
    def __repr__(self):
        return f"<USER {self.first_name} {self.last_name} ({self.email})>"
    
#mirrors guestbooks database
class Guestbook(db.Model):
    __tablename__ = 'guestbooks'

    event_id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id        = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    event_date      = db.Column(db.DateTime, nullable=False)
    event_title     = db.Column(db.Text, nullable=False)
    event_address   = db.Column(db.Text, nullable=False)
    event_img       = db.Column(db.Text)

    def __repr__(self):
        return f"<GUESTBOOK {self.event_id}: {self.event_title}@{self.event_address} STARTING {self.event_date}>"
    
#mirrors messages database
class Message(db.Model):
    __tablename__ = 'messages'

    msg_id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id        = db.Column(db.Integer, db.ForeignKey('guestbooks.event_id', ondelete="CASCADE"), nullable=False)
    display_name    = db.Column(db.Text, nullable=False)
    message_content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Message from {self.display_name}>"
