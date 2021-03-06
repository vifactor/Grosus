from app import db
from flask.ext.login import UserMixin
from sqlalchemy import UniqueConstraint

import random # FIXME: remove it when rating calculation is implemented

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    
    def __repr__(self):
        return '<User %r>' % self.login
        
    def laws_to_vote(self):
        """Returns all laws from the database. In future, it is expected that 
        laws proposed to be voted by a user will be chosen according to
        some algorithm"""
        return Law.query.all()
    
    def get_votes_count(self):
        """ returns nb of votes done by the user """
        return UserVote.query.filter(UserVote.user_id==self.id).count()

authorship = db.Table('authorship',
    db.Column('law_id', db.Integer, db.ForeignKey('law.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('deputy.id'))
    )

class Deputy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    group = db.Column(db.String(64))

    def __repr__(self):
        return '<Deputy %s (%s)>' % (self.name, self.group)
    
    def get_rating(self, user):
        # FIXME
        return random.uniform(0, 5)
    
    def vote(self, law, option, attempt=1):
        vote = DeputyVote(deputy_id = self.id, law_id = law.id,
                            attempt=attempt, option = option)
        db.session.add(vote)
        db.session.commit()
    
    def support(self, law, attempt = 1):
        self.vote(law, 1, attempt)
        
    def reject(self, law, attempt = 1):
        self.vote(law, 2, attempt)
    
    def abstain(self, law, attempt = 1):
        self.vote(law, 3, attempt)
        
    def do_not_vote(self, law, attempt = 1):
        self.vote(law, 4, attempt)
    
    def set_absent(self, law, attempt = 1):
        self.vote(law, 5, attempt)


class Law(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True)
    title = db.Column(db.String(1024))
    authors = db.relationship('Deputy',
                            secondary = authorship,
                            #primaryjoin=(followers.c.follower_id == id),
                            #secondaryjoin=(followers.c.followed_id == id),
                            backref=db.backref('laws', lazy='dynamic'),
                            lazy='dynamic')
    
    def __repr__(self):
        return '<Law %s: "%s">' % (self.code, self.title)


class DeputyVote(db.Model):
    deputy_id = db.Column(db.Integer, db.ForeignKey('deputy.id'), primary_key=True)
    law_id = db.Column(db.Integer, db.ForeignKey('law.id'), primary_key=True)
    # one law can be voted several times: this is vote attempt number
    attempt = db.Column(db.SmallInteger, primary_key=True)
    # Deputy vote options
    # 1 = support
    # 2 = reject
    # 3 = abstained
    # 4 = did not vote
    # 5 = absent
    option = db.Column(db.SmallInteger)
    
    __table_args__ = (UniqueConstraint('deputy_id', 'law_id', 'attempt',
                        name='_deputy_vote_for_law'),)
                        
                        
class UserVote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    law_id = db.Column(db.Integer, db.ForeignKey('law.id'), primary_key=True)
    # Deputy vote options
    # 1 = support
    # -1 = reject
    # 0 = ignore
    option = db.Column(db.SmallInteger)
    user = db.relationship('User', backref=db.backref('votes', lazy='dynamic'))
    law = db.relationship('Law', backref=db.backref('votes', lazy='dynamic'))
    
    __table_args__ = (UniqueConstraint('user_id', 'law_id',
                        name='_user_vote_for_law'),)
