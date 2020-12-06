from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DBManager():
    @staticmethod
    def commitSession():
        db.session.commit()

class ModelHelper():
    def save(self):
        db.session.add(self)