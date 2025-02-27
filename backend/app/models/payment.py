from app import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payment'

    payment_id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(255))
    payment_status = db.Column(db.String(255))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, total_price, payment_method=None, payment_status=None, payment_date=None):
        self.total_price = total_price
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.payment_date = payment_date if payment_date else datetime.utcnow()

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
