from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"

from .util import ListConverter

app.url_map.converters['list'] = ListConverter
app.config["SECRET_KEY"] = '8e32962d3ed1bc103e804b9136281acd'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["UPLOAD_FOLDER"] = 'static/savegames'
with open("files/tags.txt", "r", encoding = 'utf-8') as tags:
    app.config["LOCALISATION_DICT"] = eval(tags.read())
db = SQLAlchemy(app)
login_manager.init_app(app)

from statstool_web import routes
