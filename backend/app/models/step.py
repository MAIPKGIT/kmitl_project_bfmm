from app import db

class Step(db.Model):
    __tablename__ = 'step'

    id = db.Column(db.Integer, primary_key=True)
    step = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255))
    menu_id = db.Column(db.Integer, nullable=False)

    def __init__(self, step, menu_id, description=None):
        self.step = step
        self.menu_id = menu_id
        self.description = description

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
