from app import db
from datetime import datetime

class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, menu_id, quantity, total, time_stamp=None):
        self.menu_id = menu_id
        self.quantity = quantity
        self.total = total
        self.time_stamp = time_stamp or datetime.utcnow()

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
