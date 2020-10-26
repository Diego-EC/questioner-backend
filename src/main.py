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

#region role_endpoints
@app.route('/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    all_roles = list(map(lambda x: x.serialize(), roles))

    return jsonify(all_roles), 200
#endregion

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

@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    request_body = request.get_json()
    user = User.query.get(id)
    if user is None:
        raise APIException('User not found', status_code=404)
    if "name" in request_body:
        user.name = request_body["name"]
    if "email" in request_body:
        user.email = request_body["email"]
    if "password" in request_body:
        user.password = request_body["password"]
    now = datetime.datetime.now()
    user.last_update = now
    db.session.commit() 
    return "User updated", 200

@app.route('/user-is-active/<int:id>', methods=['PUT'])
def update_user_is_active(id):
    request_body = request.get_json()
    user = User.query.get(id)
    if user is None:
        raise APIException('User not found', status_code=404)
    if "is_active" in request_body:
        user.is_active = request_body["is_active"]
    now = datetime.datetime.now()
    user.last_update = now
    db.session.commit() 
    return "User is_active updated", 200
#endregion

#region question_endpoints
@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    all_questions = list(map(lambda x: x.serialize(), questions))
    return jsonify(all_questions), 200

@app.route('/question', methods=['POST'])
def add_question():
    request_body = request.get_json()
    now = datetime.datetime.now()
    question = Question(id_user=request_body["id_user"], title=request_body["title"], 
    description=request_body["description"], link=request_body["link"], created=now, last_update=now)
    db.session.add(question)
    db.session.commit()    
    return "Question added", 200

@app.route('/question/<int:id>', methods=['PUT'])
def update_question(id):
    request_body = request.get_json()
    question = Question.query.get(id)
    if question is None:
        raise APIException('Question not found', status_code=404)
    if "title" in request_body:
        question.title = request_body["title"]
    if "description" in request_body:
        question.description = request_body["description"]
    if "link" in request_body:
        question.link = request_body["link"]
    now = datetime.datetime.now()
    question.last_update = now
    db.session.commit() 
    return "Question updated", 200

@app.route('/question/<int:id>', methods=['DELETE'])
def delete_question(id):
    question = Question.query.get(id)
    if question is None:
        raise APIException('Question not found', status_code=404)
    db.session.delete(question)
    db.session.commit() 
    return "Question deleted", 200
#endregion

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
        raise APIException('User with the email ' + email + ' not found', status_code=404)
    all_answers = list(map(lambda x: x.serialize(), answers))
    return jsonify(all_answers), 200

@app.route('/answer', methods=['POST'])
def add_answer():
    request_body = request.get_json()
    now = datetime.datetime.now()
    answer = Answer(id_question=request_body["id_question"], id_user=request_body["id_user"],  
    description=request_body["description"], link=request_body["link"], created=now, last_update=now)
    db.session.add(answer)
    db.session.commit()    
    return "Answer added", 200

@app.route('/answer/<int:id>', methods=['PUT'])
def update_answer(id):
    request_body = request.get_json()
    answer = Answer.query.get(id)
    if answer is None:
        raise APIException('Answer not found', status_code=404)
    if "description" in request_body:
        answer.description = request_body["description"]
    if "link" in request_body:
        answer.link = request_body["link"]
    now = datetime.datetime.now()
    answer.last_update = now
    db.session.commit() 
    return "Answer updated", 200

@app.route('/answer/<int:id>', methods=['DELETE'])
def delete_answer(id):
    answer = Answer.query.get(id)
    if answer is None:
        raise APIException('Answer not found', status_code=404)
    db.session.delete(answer)
    db.session.commit() 
    return "Answer deleted", 200
#endregion

#region question_image_endpoints
@app.route('/question-images', methods=['GET'])
def get_question_images():
    question_images = Question_Images.query.all()
    all_question_images = list(map(lambda x: x.serialize(), question_images))
    return jsonify(all_question_images), 200

@app.route('/question-images-by-question-id/<int:id>', methods=['GET'])
def get_question_images_by_question_id(id):
    question_images = Question_Images.query.filter_by(id_question=id).all()
    all_question_images = list(map(lambda x: x.serialize(), question_images))
    return jsonify(all_question_images), 200

@app.route('/question-images', methods=['POST'])
def add_question_image():
    request_body = request.get_json()
    now = datetime.datetime.now()
    question_image = Question_Images(id_question=request_body["id_question"], url=request_body["url"],
    size=request_body["size"], created=now, last_update=now)
    db.session.add(question_image)
    db.session.commit()    
    return "Question Image added", 200

@app.route('/question-image/<int:id>', methods=['DELETE'])
def delete_question_image(id):
    question_image = Question_Images.query.get(id)
    if question_image is None:
        raise APIException('Question_Image not found', status_code=404)
    db.session.delete(question_image)
    db.session.commit() 
    return "Question_Image deleted", 200

@app.route('/question-images-delete-by-question-id/<int:id>', methods=['DELETE'])
def delete_question_image_by_question_id(id):
    db.session.query(Question_Images).filter(Question_Images.id_question == id).delete(synchronize_session=False)
    db.session.commit()
    return "Question_Images deleted", 200
#endregion

#region answer_image_endpoints
@app.route('/answer-images', methods=['GET'])
def get_answer_images():
    answer_images = Answer_Images.query.all()
    all_answer_images = list(map(lambda x: x.serialize(), answer_images))
    return jsonify(all_answer_images), 200

@app.route('/answer-images-by-answer-id/<int:id>', methods=['GET'])
def get_answer_images_by_answer_id(id):
    answer_images = Answer_Images.query.filter_by(id_answer=id).all()
    all_answer_images = list(map(lambda x: x.serialize(), answer_images))
    return jsonify(all_answer_images), 200

@app.route('/answer-images', methods=['POST'])
def add_answer_image():
    request_body = request.get_json()
    now = datetime.datetime.now()
    answer_image = Answer_Images(id_answer=request_body["id_answer"], url=request_body["url"],
    size=request_body["size"], created=now, last_update=now)
    db.session.add(answer_image)
    db.session.commit()    
    return "Answer Image added", 200

@app.route('/answer-image/<int:id>', methods=['DELETE'])
def delete_answer_image(id):
    answer_image = Answer_Images.query.get(id)
    if answer_image is None:
        raise APIException('Answer_Image not found', status_code=404)
    db.session.delete(answer_image)
    db.session.commit() 
    return "Answer_Image deleted", 200

@app.route('/answer-images-delete-by-answer-id/<int:id>', methods=['DELETE'])
def delete_answer_image_by_answer_id(id):
    db.session.query(Answer_Images).filter(Answer_Images.id_answer == id).delete(synchronize_session=False)
    db.session.commit()
    return "Answer_Images deleted", 200
#endregion

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)