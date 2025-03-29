# mirrors the guestbooks database for easier writing/reading
from extensions import db

class Guestbook(db.Model):
    __tablename__ = 'guestbooks'

    event_id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id        = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    event_date      = db.Column(db.DateTime, nullable=False)
    event_title     = db.Column(db.Text, nullable=False)
    event_address   = db.Column(db.Text, nullable=False)
    event_img       = db.Column(db.Text)

    def __repr__(self):
        return f"<Guestbook {self.event_title}>"