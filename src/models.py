from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    
    def __repr__(self):
        return '<Role %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    id_role = db.Column(db.Integer, db.ForeignKey("role.id"))
    is_active = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    alerts_activated = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    role = db.relationship('Role', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "id_role": self.id_role
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey("user.id"))
    title = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(1000), unique=False, nullable=False)
    link = db.Column(db.String(120), unique=False, nullable=True)
    is_answer_selected = db.Column(db.Integer, db.ForeignKey("answer.id"))
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    user = db.relationship('User', lazy=True)
    answer = db.relationship('Answer', foreign_keys=[is_answer_selected])

    def __repr__(self):
        return '<Question %r>' % self.title

    def serialize(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "title": self.title,
            "description": self.description
        }

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_question = db.Column(db.Integer, db.ForeignKey("question.id"))
    id_user = db.Column(db.Integer, db.ForeignKey("user.id"))
    description = db.Column(db.String(1000), unique=False, nullable=False)
    link = db.Column(db.String(120), unique=False, nullable=True)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    question = db.relationship("Question", foreign_keys=[id_question])
    user = db.relationship("User", foreign_keys=[id_user])

    def __repr__(self):
        return '<Answer %r>' % self.title

    def serialize(self):
        return {
            "id": self.id,
            "id_question": self.id_question,
            "id_user": self.id_user,
            "description": self.description
        }

class Question_Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_question = db.Column(db.Integer, db.ForeignKey("question.id"))
    url = db.Column(db.String(120), unique=False, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=True)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    question = db.relationship("Question", foreign_keys=[id_question])

    def __repr__(self):
        return '<Question_Images %r>' % self.title

    def serialize(self):
        return {
            "id": self.id,
            "id_question": self.id_question,
            "url": self.url,
            "size": self.size,
            "created": self.created,
            "last_update": self.last_update
        }

class Answer_Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_answer = db.Column(db.Integer, db.ForeignKey("answer.id"))
    url = db.Column(db.String(120), unique=False, nullable=False)
    size = db.Column(db.Integer, unique=False, nullable=True)
    created = db.Column(db.DateTime(), unique=False, nullable=False)
    last_update = db.Column(db.DateTime(), unique=False, nullable=False)
    question = db.relationship("Answer", foreign_keys=[id_answer])

    def __repr__(self):
        return '<Answer_Images %r>' % self.title

    def serialize(self):
        return {
            "id": self.id,
            "id_answer": self.id_question,
            "url": self.url,
            "size": self.size,
            "created": self.created,
            "last_update": self.last_update
        }