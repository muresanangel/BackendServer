import mimetypes
import re
from flask import Flask, jsonify, request, send_file, make_response, redirect
from flask_cors import CORS
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
import base64
import io
import PIL.Image as Image

from models.pets import PetModel
from models.users import UserModel
from db import db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
app.config['JWT_SECRET_KEY'] = 'sm8dfr8nmneh1q2'
cors = CORS(app, supports_credentials=True, expose_headers="Date, Server, Set-Cookie")

@event.listens_for(Engine, "connect")  #activam constrangerea pentru foreign key in sqlite
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

@app.before_first_request
def create_tables():
   	db.create_all()

jwt = JWTManager(app)

# @jwt.token_in_blacklist_loader
# def check_if_token_in_blacklist(decrypted_token):
#     jti = decrypted_token['jti']
#     return RevokedTokenModel.is_jti_blacklisted(jti)

def get_pet_request_headers(request):
    req_name = request.headers.get('name', None)
    req_age = request.headers.get('age', None)
    req_sex = request.headers.get('sex', None)
    req_neuter = request.headers.get('neuter', None)
    req_story = request.headers.get('story', None)
    req_remarks = request.headers.get('remarks', None)
    
    pic = request.files.get('img', None)
    
    return req_name, req_age, req_sex, req_neuter, req_story, req_remarks, pic

def get_bool_from_req(req_bool_string):
    if req_bool_string == 'True':
        return True
    return False

@app.route('/addPet', methods=['POST'])
@jwt_required()
def add_pet():
    req_name, req_age, req_sex, req_neuter, req_story, req_remarks, pic = get_pet_request_headers(request)

    if req_name is None:
        return "No name provided", 400
    
    if req_age is None:
        return "No age provided", 400
    
    if req_sex is None:
        return "No sex provided", 400
    
    if req_neuter is None:
        return "No neuter information provided", 400
    else:
        req_neuter = get_bool_from_req(req_neuter)
    
    if req_story is None:
        return "No story provided", 400
    
    if req_remarks is None:
        return "No remark provided", 400
    
    if pic is None:
        return "No image provided", 400
    
    filename =  secure_filename(pic.filename)
    req_mimetypes = pic.mimetype
    
    pet = PetModel(name = req_name, age = req_age, sex = req_sex, neuter = req_neuter, story = req_story, remarks = req_remarks, img = pic.read(), img_mimetype = req_mimetypes)
    try:
        pet.save_to_db()
    except:
        return "An error occurred while adding the pet", 500
    
    return 'Pet added successfully', 201

@app.route('/getPet', methods=['GET'])
@jwt_required()
def get_pet():
    req_id = request.headers.get('id', None)
    
    if req_id is None:
        return "No pet id provided", 400
    
    crt_pet = PetModel.find_by_id(req_id)
    if crt_pet:
        return crt_pet.json(), 200
        # crt_pet = crt_pet.json()
        # extension = mimetypes.guess_extension(crt_pet['mimetype'])
        # img_data = base64.b64decode(crt_pet['image'])
        # image = Image.open(io.BytesIO(img_data))
        # image.save('./image' + extension)
    return 'No pet found', 404

@app.route('/get_all_pets', methods=['GET'])
@jwt_required()
def get_all_pets():
    return {'pets': [pet.json() for pet in PetModel.find_all()]}

@app.route('/delete_pet', methods=['DELETE'])
@jwt_required()
def delete_pet():
    req_id = request.headers.get('id', None)
    
    if req_id is None:
        return "No pet id provided", 400
    
    crt_pet = PetModel.find_by_id(req_id)
    if crt_pet:
        try:
            crt_pet.delete_from_db()
        except:
            return "An error occurred while deleting the pet", 500
    return "Pet deleted successfully", 200

@app.route('/edit_pet', methods=['PUT'])
@jwt_required()
def edit_pet():
    req_id = request.headers.get('id', None)
    
    if req_id is None:
        return "No pet id provided", 400
    
    crt_pet = PetModel.find_by_id(req_id)
    
    req_name, req_age, req_sex, req_neuter, req_story, req_remarks, pic = get_pet_request_headers(request)
    
    if req_name:
        crt_pet.name = req_name
    
    if req_age:
        crt_pet.age = req_age
    
    if req_sex:
        crt_pet.sex = req_sex
    
    if req_neuter:
        req_neuter = get_bool_from_req(req_neuter)
        crt_pet.neuter = req_neuter
    
    if req_story:
        crt_pet.story = req_story
    
    if req_remarks:
        crt_pet.remarks = req_remarks
    
    if pic:
        crt_pet.img = pic.read()
        crt_pet.img_mimetype = pic.mimetype
    
    try:
        db.session.commit()
    except:
        return "An error occurred while updating the pet", 500
    
    return 'Pet edited successfully', 201

@app.route('/login', methods=['POST'])
def login():
    req_email = request.headers.get('email', None)
    req_password = request.headers.get('password', None)
    print(req_email)
    print(req_password)
    if req_email is None:
        return 'No email address provided', 400
    if req_password is None:
        return 'Password is required', 400
    
    user = UserModel.find_by_email(req_email)
    if user:
        if UserModel.verify_hash(req_password, user.password):
            access_token = create_access_token(identity=user.user_id)
            return {
                'login': True,
                'access_token': access_token
            }, 200
        else:
            return 'Password is incorrect', 400
    else:
        return 'There is no user with the provided email address', 400

@app.route('/add_admin', methods=['POST'])
@jwt_required()
def add_admin():
    user_id = get_jwt_identity()
    userCrt = UserModel.find_by_id(user_id)
    
    if userCrt.is_super_admin():
        req_email = request.headers.get('email', None)
        req_password = request.headers.get('password', None)
        req_admin = request.headers.get('admin', None)
        
        if req_email is None:
            return 'No email address provided', 400
        if req_password is None:
            return 'Password is required', 400
        if req_admin is None:
            return 'No admin information available', 400
        
        if not UserModel.find_by_email(req_email):
            req_admin = get_bool_from_req(req_admin)
            user = UserModel(req_email, UserModel.generate_hash(req_password), req_admin)
            try:
                user.save_to_db()
            except:
                return {'message': 'An error occurred while adding the user into the database'}, 500
            return {'message': 'User added succesfully'}, 201
        
        return "Email already exists", 400
    return "You don't have the necessary permissions", 400

@app.route('/get_admin', methods=['GET'])
@jwt_required()
def get_admin():
    user_id = get_jwt_identity()
    userCrt = UserModel.find_by_id(user_id)
    
    if userCrt.is_super_admin():
        req_id = request.headers.get('id', None)
    
        if req_id is None:
            return "No admin id provided", 400
        
        src_admin = UserModel.find_by_id(req_id)
        if src_admin:
            return src_admin.json(), 200
        return "There is no admin with the specified id", 404
    
    return "You don't have the necessary permissions", 400

@app.route('/get_all_admins', methods=['GET'])
@jwt_required()
def get_all_admins():
    user_id = get_jwt_identity()
    userCrt = UserModel.find_by_id(user_id)
    
    if userCrt.is_super_admin():
        return {'admins': [admin.json() for admin in UserModel.find_all()]}
    
    return "You don't have the necessary permissions", 400

@app.route('/delete_admin', methods=['DELETE'])
@jwt_required()
def delete_admin():
    user_id = get_jwt_identity()
    userCrt = UserModel.find_by_id(user_id)
    
    if userCrt.is_super_admin():
        req_id = request.headers.get('id', None)
    
        if req_id is None:
            return "No pet id provided", 400
        
        src_admin = UserModel.find_by_id(req_id)
        if src_admin:
            print(src_admin.is_super_admin())
            if not src_admin.is_super_admin():
                try:
                    src_admin.delete_from_db()
                except:
                    return "An error occurred while deleting the admin", 500
                return "Admin deleted successfully", 200
            return "Super Admins cannot be deleted", 400
        return "There is no admin with the specified id", 404
    
    return "You don't have the necessary permissions", 400

if __name__ == '__main__':
    db.init_app(app)
    app.run(host = '0.0.0.0',port = 5000, debug = True)