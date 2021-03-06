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
from models import db, User, Role, Question, Answer, QuestionImages, AnswerImages
from helpers import DBManager
import datetime
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from aws import upload_file_to_s3
from sqlalchemy import and_, or_, not_

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = '546asdf8965as4f6987wetr654'
jwt = JWTManager(app)

app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=30)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.cli.command("create-roles")
def create_roles():
    print("create_roles")
    now = datetime.datetime.now()
    if not Role.query.get(1):
        role = Role(id=1, name="Admin", created=now, last_update=now)
        role.save()
    if not Role.query.get(2):
        role = Role(id=2, name="User", created=now, last_update=now)
        role.save()
    DBManager.commitSession()
    return

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)
    #return "", 200

#region login_logout
@app.route('/login', methods=['POST'])
def login():
    status = "KO"
    if not request.is_json:
        return jsonify({"status": status, "msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not email:
        return jsonify({"status": status, "msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"status": status, "msg": "Missing password parameter"}), 400

    user = User.query.filter_by(email=email).filter_by(password=password).filter_by(is_active=True).one_or_none()

    if user is None:
        return jsonify({"status": status, "msg": "Bad username or password"}), 401

    status = "OK"
    access_token = create_access_token(identity=user.id)
    return jsonify({"status": status, "access_token": access_token, "user": user.serialize()}), 200

@app.route('/check-protected', methods=['POST'])
@jwt_required
def check_protected():
    user_id  = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({"status": "OK", "logged_in_as": user.serialize()}), 200

@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({"status": "OK"}), 200
#endregion

#region role_endpoints
@app.route('/roles', methods=['GET'])
@jwt_required
def get_roles():
    roles = Role.query.all()
    all_roles = list(map(lambda x: x.serialize(), roles))

    return jsonify(all_roles), 200
#endregion

#region user_endpoints
@app.route('/user/<int:id>', methods=['GET'])
@jwt_required
def get_user(id):
    user = User.query.get(id)
    return user.serialize(), 200

@app.route('/user-by-email/<string:email>', methods=['GET'])
@jwt_required
def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if user is None:
        raise APIException('User with the email ' + email + ' not found', status_code=400)
    return user.serialize(), 200

@app.route('/users', methods=['GET'])
@jwt_required
def get_users():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200

@app.route('/user', methods=['POST'])
def add_user():
    request_body = request.get_json()
    now = datetime.datetime.now()
    user = User(name=request_body["name"], email=request_body["email"], password=request_body["password"], id_role=2, created=now, last_update=now)
    user.save()
    DBManager.commitSession()
    return jsonify("User added"), 200

@app.route('/user/<int:id>', methods=['PUT'])
@jwt_required
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
    return jsonify("User updated"), 200

@app.route('/user-is-active', methods=['PUT'])
@jwt_required
def update_user_is_active():
    request_body = request.get_json()
    user = User.query.get(request_body["id_user"])
    if user is None:
        raise APIException('User not found', status_code=404)
    if "is_active" in request_body:
        user.is_active = request_body["is_active"]
    now = datetime.datetime.now()
    user.last_update = now
    db.session.commit() 
    return jsonify("User is_active updated"), 200
#endregion user_endpoints

#region question_endpoints
@app.route('/questions', methods=['GET'])
@jwt_required
def get_questions():
    questions = Question.query.all()
    all_questions = list(map(lambda x: x.serialize(), questions))
    for x in all_questions:
        number = Answer.query.filter_by(id_question=x["id"]).count()
        x["number_of_answers"] = number
        user = User.query.filter_by(id=x["id_user"]).first()
        x["user_name"] = user.name
    return jsonify(all_questions), 200

@app.route('/question/<int:id>', methods=['GET'])
@jwt_required
def get_question(id):
    question = Question.query.get(id)
    if question is None:
        raise APIException('Question not found', status_code=404)
    return jsonify(question.serialize_with_user()), 200

@app.route('/question', methods=['POST'])
@jwt_required
def add_question():
    request_body = request.get_json()
    now = datetime.datetime.now()
    question = Question(id_user=request_body["id_user"], title=request_body["title"], 
    description=request_body["description"], link=request_body["link"], created=now, last_update=now)
    question.save()
    DBManager.commitSession()
    return jsonify({"status": "OK", "msg": "Question added", "question": question.serialize()}), 200

@app.route('/question/<int:id>', methods=['PUT'])
@jwt_required
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
    return jsonify("Question updated"), 200

@app.route('/question/<int:id>', methods=['DELETE'])
@jwt_required
def delete_question(id):
    question = Question.query.get(id)
    if question is None:
        raise APIException('Question not found', status_code=404)

    answers = Answer.query.filter_by(id_question=id).all()
    for answer in answers:
        db.session.delete(answer)

    db.session.delete(question)
    db.session.commit() 
    return jsonify("Question deleted"), 200

@app.route('/mark-best-answer', methods=['PUT'])
@jwt_required
def mark_best_answer():
    request_body = request.get_json()
    question = Question.query.get(request_body["id_question"])
    if question is None:
        raise APIException('Question not found', status_code=404)
    answer = Answer.query.get(request_body["id_answer"])
    if answer is None:
        raise APIException('Answer not found', status_code=404)
    question.id_answer_selected = request_body["id_answer"]
    db.session.commit() 
    return jsonify("Answer marked"), 200

@app.route('/search-questions-by-string/<string:searchText>', methods=['GET'])
@jwt_required
def get_search_questions_by_string(searchText):
    words = searchText.split(' ')

    filters = []
    for word in words:
        if len(word) >= 3:
            word_like = "%{}%".format(word)
            filters.append(Question.title.ilike(word_like))
            filters.append(Question.description.ilike(word_like))
    questions = Question.query.filter(or_(*filters)).all()
    all_questions = list(map(lambda x: x.serialize(), questions))
    for x in all_questions:
        number = Answer.query.filter_by(id_question=x["id"]).count()
        x["number_of_answers"] = number
        user = User.query.filter_by(id=x["id_user"]).first()
        x["user_name"] = user.name
    return jsonify({"status": "OK", "msg": "Search result", "questions": all_questions}), 200
#endregion question_endpoints

#region answer_endpoints
@app.route('/answers', methods=['GET'])
@jwt_required
def get_answers():
    answers = Answer.query.all()
    all_answers = list(map(lambda x: x.serialize(), answers))
    for x in all_answers:
        user = User.query.filter_by(id=x["id_user"]).first()
        x["user_name"] = user.name
    return jsonify(all_answers), 200

@app.route('/answer/<int:id>', methods=['GET'])
@jwt_required
def get_answer(id):
    answer = Answer.query.get(id)
    if answer is None:
        raise APIException('Answer not found', status_code=404)
    return jsonify(answer.serialize()), 200

@app.route('/answers-by-question-id/<int:id>', methods=['GET'])
@jwt_required
def answers_by_question_id(id):
    answers  = Answer.query.filter_by(id_question=id).all() 
    if answers is None:
        raise APIException('User with the email ' + email + ' not found', status_code=404)
    all_answers = list(map(lambda x: x.serialize(), answers))
    for x in all_answers:
        user = User.query.filter_by(id=x["id_user"]).first()
        x["user_name"] = user.name
    return jsonify(all_answers), 200

@app.route('/answer', methods=['POST'])
@jwt_required
def add_answer():
    request_body = request.get_json()
    now = datetime.datetime.now()
    answer = Answer(id_question=request_body["id_question"], id_user=request_body["id_user"],  
    description=request_body["description"], link=request_body["link"], created=now, last_update=now)
    answer.save()
    DBManager.commitSession()
    return jsonify({"status": "OK", "msg": "Answer added", "answer": answer.serialize()}), 200
    #return jsonify("Answer added"), 200

@app.route('/answer/<int:id>', methods=['PUT'])
@jwt_required
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
    #return jsonify("Answer updated"), 200
    return jsonify({"status": "OK", "msg": "Updated added", "answer": answer.serialize()}), 200

@app.route('/answer/<int:id>', methods=['DELETE'])
@jwt_required
def delete_answer(id):
    print("--> delete")
    print(id)
    answer = Answer.query.get(id)
    print(answer)
    if answer is None:
        raise APIException('Answer not found', status_code=404)
    db.session.delete(answer)
    print("->deleted")
    db.session.commit() 
    print("->commit")
    return jsonify("Answer deleted"), 200
#endregion

#region question_image_endpoints
@app.route('/question-images', methods=['GET'])
@jwt_required
def get_question_images():
    question_images = QuestionImages.query.all()
    all_question_images = list(map(lambda x: x.serialize(), question_images))
    return jsonify(all_question_images), 200

@app.route('/question-images-by-question-id/<int:id>', methods=['GET'])
@jwt_required
def get_question_images_by_question_id(id):
    question_images = QuestionImages.query.filter_by(id_question=id).all()
    all_question_images = list(map(lambda x: x.serialize(), question_images))
    return jsonify(all_question_images), 200

@app.route('/question-images', methods=['POST'])
@jwt_required
def add_question_image():
    request_body = request.get_json()
    now = datetime.datetime.now()
    question_image = QuestionImages(id_question=request_body["id_question"], url=request_body["url"],
    size=request_body["size"], created=now, last_update=now)
    question_image.save()
    DBManager.commitSession()   
    return jsonify("Question Image added"), 200

@app.route('/question-image/<int:id>', methods=['DELETE'])
@jwt_required
def delete_question_image(id):
    question_image = QuestionImages.query.get(id)
    if question_image is None:
        raise APIException('QuestionImage not found', status_code=404)
    db.session.delete(question_image)
    db.session.commit() 
    return jsonify("QuestionImage deleted"), 200

@app.route('/question-images-delete-by-question-id/<int:id>', methods=['DELETE'])
@jwt_required
def delete_question_image_by_question_id(id):
    db.session.query(QuestionImages).filter(QuestionImages.id_question == id).delete(synchronize_session=False)
    db.session.commit()
    return jsonify("QuestionImages deleted"), 200
#endregion

#region answer_image_endpoints
@app.route('/answer-images', methods=['GET'])
@jwt_required
def get_answer_images():
    answer_images = AnswerImages.query.all()
    all_answer_images = list(map(lambda x: x.serialize(), answer_images))
    return jsonify(all_answer_images), 200

@app.route('/answer-images-by-answer-id/<int:id>', methods=['GET'])
@jwt_required
def get_answer_images_by_answer_id(id):
    answer_images = AnswerImages.query.filter_by(id_answer=id).all()
    all_answer_images = list(map(lambda x: x.serialize(), answer_images))
    return jsonify(all_answer_images), 200

@app.route('/answer-images', methods=['POST'])
@jwt_required
def add_answer_image():
    request_body = request.get_json()
    now = datetime.datetime.now()
    answer_image = AnswerImages(id_answer=request_body["id_answer"], url=request_body["url"],
    size=request_body["size"], created=now, last_update=now)
    answer_image.save()
    DBManager.commitSession()
    return jsonify("Answer Image added"), 200

@app.route('/answer-image/<int:id>', methods=['DELETE'])
@jwt_required
def delete_answer_image(id):
    answer_image = AnswerImages.query.get(id)
    if answer_image is None:
        raise APIException('AnswerImage not found', status_code=404)
    db.session.delete(answer_image)
    db.session.commit() 
    return jsonify("AnswerImage deleted"), 200

@app.route('/answer-images-delete-by-answer-id/<int:id>', methods=['DELETE'])
@jwt_required
def delete_answer_image_by_answer_id(id):
    db.session.query(AnswerImages).filter(AnswerImages.id_answer == id).delete(synchronize_session=False)
    db.session.commit()
    return jsonify("AnswerImages deleted"), 200
#endregion

#region upload_images
@app.route('/upload-question-images', methods=['POST'])
#@jwt_required
def upload_question_images():
    print("upload_question_images")
    files = request.files
    print(files)
    id_question = request.form.get('id_question')
    for key in files:
        print(key)
        file = files[key]
        if file:
            print(file)
            url_image = upload_file_to_s3(file, os.environ.get('S3_BUCKET_NAME'))
            print(url_image)
            now = datetime.datetime.now()
            question_image = QuestionImages(id_question=id_question, url=url_image, 
            size=0, created=now, last_update=now)
            question_image.save()
            DBManager.commitSession()
    return jsonify("OK"), 200

@app.route('/upload-answer-images', methods=['POST'])
#@jwt_required
def upload_answer_images():
    files = request.files
    id_answer = request.form.get('id_answer')
    for key in files:
        file = files[key]
        if file:
            url_image = upload_file_to_s3(file, os.environ.get('S3_BUCKET_NAME'))
            now = datetime.datetime.now()
            answer_image = AnswerImages(id_answer=id_answer, url=url_image, 
            size=0, created=now, last_update=now)
            answer_image.save()
            DBManager.commitSession()
    return jsonify("OK"), 200
#endregion

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)