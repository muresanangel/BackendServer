from db import db


class ImageModel(db.Model):
    __tablename__ = 'images'

    img_id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, nullable=False, unique=True)
    mimetype = db.Column(db.Text, nullable=False)
    
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.pet_id', ondelete='CASCADE'))

    def __init__(self, data, pet_id):
        self.data = data
        self.pet_id = pet_id
    
    def json(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'mimetype': self.mimetype,
            'img': self.img
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_pet_id(cls, _id):
        return cls.query.filter_by(pet_id=_id).first()
    
    @classmethod
    def find_all(cls):
        return cls.query.all()