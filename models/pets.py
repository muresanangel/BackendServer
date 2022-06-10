from db import db
import base64

class PetModel(db.Model):
    __tablename__ = 'pets'

    pet_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(20))
    neuter = db.Column(db.Boolean)
    story = db.Column(db.String(255))
    remarks = db.Column(db.String(255))
    img = db.Column(db.Text, nullable=False)
    img_mimetype = db.Column(db.Text, nullable=False)

    # images =  db.relationship('ImageModel', backref='parent', lazy='dynamic', passive_deletes=True)

    def __init__(self, name, age, sex, neuter, story, remarks, img, img_mimetype):
        self.name = name
        self.age = age
        self.sex = sex
        self.neuter = neuter
        self.story = story
        self.remarks = remarks
        self.img = img
        self.img_mimetype = img_mimetype
    
    def json(self): #functie pentru returnarea unui sistem cu toate informatiile despre acesta
        return {
            'name': self.name,
            'age': self.age,
            'sex': self.sex,
            'neuter': self.neuter,
            'story': self.story,
            'remarks': self.remarks,
            'image': base64.encodebytes(self.img).decode(),
            'mimetype': self.img_mimetype
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(pet_id=_id).first()
    
    @classmethod
    def find_all(cls):
        return cls.query.all()