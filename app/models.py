from app import db
from flask.ext.login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    
    def __repr__(self):
        return '<User %r>' % self.login

class Deputy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    group = db.Column(db.String(64), index=True)

    def __repr__(self):
        return '<Deputy %s (%s)>' % self.name, self.group
    
    def get_rating(user_id):
        # FIXME
        return 0
