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
#from models import Person

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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))

    return jsonify(all_users), 200

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

@app.route('/answers', methods=['GET'])
def get_answers():
    answers = Answer.query.all()
    all_answers = list(map(lambda x: x.serialize(), answers))

    return jsonify(all_answers), 200

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
