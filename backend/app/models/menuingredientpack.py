from app import db

class MenuIngredientPack(db.Model):
    __tablename__ = 'menuingredientpack'

    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)
    ingredient_pack_id = db.Column(db.Integer, db.ForeignKey('ingredientpack.id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def __init__(self, menu_id, ingredient_pack_id, qty):
        self.menu_id = menu_id
        self.ingredient_pack_id = ingredient_pack_id
        self.qty = qty

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
