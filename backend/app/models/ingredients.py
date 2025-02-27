from app import db
from datetime import datetime

class Ingredients(db.Model):
    __tablename__ = 'ingredients'

    Ingredients_id = db.Column(db.Integer, primary_key=True)
    Ingredients_name = db.Column(db.String(255), nullable=False)
    Ingredients_image = db.Column(db.String(255))
    Ingredients_des = db.Column(db.String(255))
    main_stock = db.Column(db.Integer)
    sub_stock = db.Column(db.Integer)
    unit = db.Column(db.String(255))
    enable = db.Column(db.Integer, default=1)  # เปลี่ยนเป็น Integer แทน Boolean

    def __init__(self, Ingredients_name, Ingredients_image=None, Ingredients_des=None, main_stock=None, sub_stock=None, unit=None, enable=1):
        self.Ingredients_name = Ingredients_name
        self.Ingredients_image = Ingredients_image
        self.Ingredients_des = Ingredients_des
        self.main_stock = main_stock
        self.sub_stock = sub_stock
        self.unit = unit
        self.enable = enable  # ค่าเริ่มต้นเป็น 1 (เปิดใช้งาน)
    
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

