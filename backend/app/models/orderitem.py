from app import db
from datetime import datetime

class OrderItem(db.Model):
    __tablename__ = 'orderitem'

    order_item_id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, nullable=False)
    menu_qty = db.Column(db.Integer, nullable=False)
    menu_note = db.Column(db.String(255))
    round_order = db.Column(db.Integer)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    order_id = db.Column(db.Integer)
    status_order = db.Column(db.String(255))
    status_serve = db.Column(db.String(255))
    finish_date = db.Column(db.DateTime)

    def __init__(self, menu_id, menu_qty, menu_note=None, round_order=None, create_date=None, order_id=None, status_order=None, status_serve=None, finish_date=None):
        self.menu_id = menu_id
        self.menu_qty = menu_qty
        self.menu_note = menu_note
        self.round_order = round_order
        self.create_date = create_date if create_date else datetime.utcnow()
        self.order_id = order_id
        self.status_order = status_order
        self.status_serve = status_serve
        self.finish_date = finish_date

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
