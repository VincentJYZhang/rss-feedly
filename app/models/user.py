from datetime import datetime
from app import db

class User(db.Model):

    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, unique=True)
    user_pass = db.Column(db.String)
    user_mail = db.Column(db.String)
    user_tel = db.Column(db.Integer)
    user_create = db.Column(db.DateTime, default=datetime.now)
    user_family_id = db.Column(db.Integer, db.ForeignKey('family.family_id'))
    user_family_confirm = db.Column(db.Boolean, default=False)

    medicines = db.relationship('Medicine', backref='user')

    def __init__(self, user_name, user_pass, user_mail="", user_tel="", fammily_id = 1):
        self.user_name = user_name
        self.user_pass = user_pass
        self.user_mail = user_mail
        self.user_tel = user_tel
        self.user_family_id = fammily_id

    def __repr__(self):
        return '<User %r>' % self.user_name

    def __str__(self):
        return '<User %s>' % self.user_name