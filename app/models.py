from app import db
from flask.ext.login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    
    def __repr__(self):
        return '<User %r>' % self.login

authorship = db.Table('authorship',
    db.Column('law_id', db.Integer, db.ForeignKey('law.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('deputy.id'))
    )

class Deputy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    group = db.Column(db.String(64), index=True)

    def __repr__(self):
        return '<Deputy %s (%s)>' % self.name, self.group
    
    def get_rating(user_id):
        # FIXME
        return 0

class Law(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16))
    title = db.Column(db.String(1024))
    authors = db.relationship('Deputy',
                            secondary = authorship,
                            #primaryjoin=(followers.c.follower_id == id),
                            #secondaryjoin=(followers.c.followed_id == id),
                            backref=db.backref('laws', lazy='dynamic'),
                            lazy='dynamic')
