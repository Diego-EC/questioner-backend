from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from helpers import ModelHelper

db = SQLAlchemy()

class Role(db.Model, ModelHelper):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    foo  = db.Column(db.String(255), unique=False, nullable=True)
    #print
    def __repr__(self):
        return '<Role %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "last_update": self.last_update
        }        

class User(db.Model, ModelHelper):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    id_role = db.Column(db.Integer, db.ForeignKey("role.id"))
    is_active = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    alerts_activated = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    role = db.relationship('Role', lazy=True)
    foo  = db.Column(db.String(255), unique=False, nullable=True)
    def __repr__(self):
        return '<Name %r>' % self.name        

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "id_role": self.id_role,
            "is_active": self.is_active,
            "alerts_activated": self.alerts_activated,
            "created": self.created,
            "last_update": self.last_update
        }

class Question(db.Model, ModelHelper):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey("user.id"))
    title = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(5000), unique=False, nullable=False)
    link = db.Column(db.String(255), unique=False, nullable=True)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    user = db.relationship('User', foreign_keys=[id_user])
    
    id_answer_selected = db.Column(db.Integer, db.ForeignKey("answer.id"), default=None)
    answer_selected = db.relationship("Answer", foreign_keys=[id_answer_selected])

    
    answer = db.relationship('Answer', foreign_keys="Answer.id_question")
    foo  = db.Column(db.String(255), unique=False, nullable=True)
    def __repr__(self):
        return '<id %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "title": self.title,
            "description": self.description,
            "link": self.link,
            "id_answer_selected": self.id_answer_selected,
            "created": self.created,
            "last_update": self.last_update
        }

    def serialize_with_user(self):
        question = self.serialize()
        question["user"] = self.user.serialize()
        return(question)

    def delete_answers(self):
        for answer in self.answers:
            db.session.delete(answer)


class Answer(db.Model, ModelHelper):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey("user.id"))
    description = db.Column(db.String(5000), unique=False, nullable=False)
    link = db.Column(db.String(255), unique=False, nullable=True)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    user = db.relationship("User", foreign_keys=[id_user])
    foo  = db.Column(db.String(255), unique=False, nullable=True)
    # many to many
    id_question = db.Column(db.Integer, db.ForeignKey("question.id", use_alter=True))
    question = db.relationship("Question", foreign_keys=[id_question])
    #id_question = db.relationship("Question", unique=False, foreign_keys="Question.id_answer_selected")

    def __repr__(self):
        return '<Answer %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "id_question": self.id_question,
            "id_user": self.id_user,
            "description": self.description,
            "link": self.link,
            "created": self.created,
            "last_update": self.last_update,
            "user_name": ""
        }

class QuestionImages(db.Model, ModelHelper):
    id = db.Column(db.Integer, primary_key=True)
    id_question = db.Column(db.Integer, db.ForeignKey("question.id"))
    url = db.Column(db.String(255), unique=False, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=True)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    question = db.relationship(Question, backref=backref("question", cascade="all,delete"))
    foo  = db.Column(db.String(255), unique=False, nullable=True)
    def __repr__(self):
        return '<QuestionImages %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "id_question": self.id_question,
            "url": self.url,
            "size": self.size,
            "created": self.created,
            "last_update": self.last_update
        }

class AnswerImages(db.Model, ModelHelper):
    id = db.Column(db.Integer, primary_key=True)
    id_answer = db.Column(db.Integer, db.ForeignKey("answer.id"))
    url = db.Column(db.String(255), unique=False, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=True)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    answer = db.relationship(Answer, backref=backref("answer", cascade="all,delete"))
    foo  = db.Column(db.String(255), unique=False, nullable=True)
    def __repr__(self):
        return '<AnswerImages %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "id_answer": self.id_answer,
            "url": self.url,
            "size": self.size,
            "created": self.created,
            "last_update": self.last_update
        }