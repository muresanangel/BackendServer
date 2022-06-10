from codecs import unicode_escape_decode
from enum import unique
from db import db
from passlib.hash import pbkdf2_sha256 as sha256

class UserModel(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    super_admin = db.Column(db.Boolean)
    
    def __init__(self, email, password, admin, super_admin = False):
        self.email = email
        self.password = password
        self.admin = admin
        self.super_admin = super_admin
    
    def json(self):
        return {
            'id': self.user_id,
            'email': self.email,
            'admin': self.admin,
            'super_admin': self.super_admin
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def is_admin(self):
        return self.admin == True
    
    def is_super_admin(self):
        return self.super_admin == True

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(user_id=_id).first()
    
    @classmethod
    def find_all(cls):
        return cls.query.all()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)