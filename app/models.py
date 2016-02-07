from app import db
from flask.ext.login import UserMixin
from sqlalchemy import UniqueConstraint

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
        return '<Deputy %s (%s)>' % (self.name, self.group)
    
    def get_rating(self, user_id):
        # FIXME
        return 0
    
    def accept(self, law):
        """Adds 'True' vote to the Deputy voting table"""
        vote = DeputyVote(deputy_id = self.id, law_id = law.id, vote_option = True)
        db.session.add(vote)
        db.session.commit()
        
    def reject(self, law):
        """Adds 'True' vote to the Deputy voting table"""
        vote = DeputyVote(deputy_id = self.id, law_id = law.id, vote_option = False)
        db.session.add(vote)
        db.session.commit()


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
    
    def __repr__(self):
        return '<Law %s: "%s">' % (self.code, self.title)

from sqlalchemy import Enum
class DeputyVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deputy_id = db.Column(db.Integer, db.ForeignKey('deputy.id'))
    law_id = db.Column(db.Integer, db.ForeignKey('law.id'))
    # True if law is accepted
    # False if law is rejected
    vote_option = db.Column(db.Boolean)
    
    __table_args__ = (UniqueConstraint('deputy_id', 'law_id', name='_deputy_vote_for_law'),)
