from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'order'

    order_id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer)
    table_id = db.Column(db.Integer, nullable=False)
    create_order = db.Column(db.DateTime, default=datetime.utcnow)
    number_of_people = db.Column(db.Integer, nullable=False)

    def __init__(self, payment_id, table_id, number_of_people, create_order=None):
        self.payment_id = payment_id
        self.table_id = table_id
        self.number_of_people = number_of_people
        self.create_order = create_order if create_order else datetime.utcnow()

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
