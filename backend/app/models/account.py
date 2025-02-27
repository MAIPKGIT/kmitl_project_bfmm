from app import db
from datetime import datetime

class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    mail = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    role = db.Column(db.String(255))
    create = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, password, mail=None, phone=None, role="user"):
        self.username = username
        self.password = password
        self.mail = mail
        self.phone = phone
        self.role = role

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
