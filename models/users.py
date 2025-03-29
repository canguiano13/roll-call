# mirrors the users database for easier writing/reading
from flask_sqlalchemy import SQLAlchemy
from extensions import db

class User(db.Model):
    __tablename__ = 'users'

    user_id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password_hash   = db.Column(db.Text, nullable=False)
    first_name      = db.Column(db.Text, nullable=False)
    last_name       = db.Column(db.Text, nullable=False)
    email           = db.Column(db.String(255), unique=True, nullable=False)
    profile_pic     = db.Column(db.Text)

    guestbooks = db.relationship('Guestbook', backref='owner', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"