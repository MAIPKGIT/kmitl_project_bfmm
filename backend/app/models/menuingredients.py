from app import db
from datetime import datetime

class MenuIngredients(db.Model):
    __tablename__ = 'menuingredients'

    MenuIngredients_id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.Ingredients_id'), nullable=False)
    volume = db.Column(db.Integer)
    unit = db.Column(db.String(255))

    def __init__(self, menu_id, ingredient_id, volume=None, unit=None):
        self.menu_id = menu_id
        self.ingredient_id = ingredient_id
        self.volume = volume
        self.unit = unit

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
