from app import db
from datetime import datetime

class Waste(db.Model):
    __tablename__ = 'waste'

    waste_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(255))
    price = db.Column(db.Integer)
    waste_date = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(255))
    note = db.Column(db.String(255))

    def __init__(self, item_name, quantity, unit=None, price=None, waste_date=None, reason=None, note=None):
        self.item_name = item_name
        self.quantity = quantity
        self.unit = unit
        self.price = price
        self.waste_date = waste_date or datetime.utcnow()
        self.reason = reason
        self.note = note

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
