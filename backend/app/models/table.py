from app import db
from datetime import datetime

class Table(db.Model):
    __tablename__ = 'table'

    table_id = db.Column(db.Integer, primary_key=True)
    people = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(255), nullable=False)

    def __init__(self, people, status, code):
        self.people = people
        self.status = status
        self.code = code

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
