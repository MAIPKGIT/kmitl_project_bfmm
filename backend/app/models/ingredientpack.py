from app import db

class IngredientPack(db.Model):
    __tablename__ = 'ingredientpack'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    stock = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "stock": self.stock
        }