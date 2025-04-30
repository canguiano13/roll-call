from extensions import db
from flask_login import UserMixin #use UserMixin class for login management capabilities


#mirror users database
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name      = db.Column(db.Text, nullable=False)
    last_name       = db.Column(db.Text, nullable=False)
    email           = db.Column(db.String(255), unique=True, nullable=False)
    password_hash   = db.Column(db.Text, nullable=False)
    profile_pic     = db.Column(db.Text)

    #defines a one-to-many relationship between users and guestbooks but does not affect the database schema. 
    #relationship provides a convenient way to access related objects. 
    #backref then adds a parent attribute to all Child objects (e.g guestbook.parent is the owner)
    guestbooks = db.relationship('Guestbook', backref='owner', cascade='all, delete-orphan')

    #defines the representation for User objects when printed
    def __repr__(self):
        return f'<USER {self.first_name} {self.last_name} ({self.email})>'
    
    #define implementation for login manager's get_id
    def get_id(self):
        return self.user_id