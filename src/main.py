"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Role, Question, Answer, Question_Images, Answer_Images
import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#region user_endpoints
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user.serialize(), 200

@app.route('/user-by-email/<string:email>', methods=['GET'])
def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if user is None:
        raise APIException('User with the email ' + email + ' not found', status_code=400)
    return user.serialize(), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200

@app.route('/user', methods=['POST'])
def add_user():
    request_body = request.get_json()
    now = datetime.datetime.now()
    user = User(name=request_body["name"], email=request_body["email"], password=request_body["password"], id_role=2, created=now, last_update=now)
    db.session.add(user)
    db.session.commit()    
    return "User added", 200
#endregion

@app.route('/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    all_roles = list(map(lambda x: x.serialize(), roles))

    return jsonify(all_roles), 200

@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    all_questions = list(map(lambda x: x.serialize(), questions))

    return jsonify(all_questions), 200

#region answer_endpoints
@app.route('/answers', methods=['GET'])
def get_answers():
    answers = Answer.query.all()
    all_answers = list(map(lambda x: x.serialize(), answers))

    return jsonify(all_answers), 200

@app.route('/answers-by-question-id/<int:id>', methods=['GET'])
def answers_by_question_id(id):
    answers  = Answer.query.filter_by(id_question=id).all() 
    if answers is None:
        raise APIException('User with the email ' + email + ' not found', status_code=400)
    all_answers = list(map(lambda x: x.serialize(), answers))
    return jsonify(all_answers), 200

#endregion


@app.route('/question-images', methods=['GET'])
def get_question_images():
    question_images = Question_Images.query.all()
    all_question_images = list(map(lambda x: x.serialize(), question_images))

    return jsonify(all_question_images), 200

@app.route('/answer-images', methods=['GET'])
def get_answer_images():
    answer_images = Answer_Images.query.all()
    all_answer_images = list(map(lambda x: x.serialize(), answer_images))

    return jsonify(all_answer_images), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)