from app import db

class IngredientPackItems(db.Model):
    __tablename__ = 'ingredientpackitems'

    id = db.Column(db.Integer, primary_key=True)
    ingredient_pack_id = db.Column(db.Integer, db.ForeignKey('ingredientpack.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.Ingredients_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def __init__(self, ingredient_pack_id, ingredient_id, qty):
        self.ingredient_pack_id = ingredient_pack_id
        self.ingredient_id = ingredient_id
        self.qty = qty

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
