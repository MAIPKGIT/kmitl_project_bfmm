from app import db

class MenuType(db.Model):
    __tablename__ = 'menutype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    des = db.Column(db.String(255))

    def __init__(self, name, des=None):
        self.name = name
        self.des = des

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
