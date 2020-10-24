import os
from flask_admin import Admin
from models import db, User, Role, Question, Answer, Question_Images, Answer_Images
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Role, db.session))
    admin.add_view(ModelView(Question, db.session))
    admin.add_view(ModelView(Answer, db.session))
    admin.add_view(ModelView(Question_Images, db.session))
    admin.add_view(ModelView(Answer_Images, db.session))