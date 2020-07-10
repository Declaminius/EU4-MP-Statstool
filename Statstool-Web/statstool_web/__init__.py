from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = '8e32962d3ed1bc103e804b9136281acd'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["UPLOAD_FOLDER"] = 'savegames'
with open("files/tags.txt", "r", encoding = 'utf-8') as tags:
    app.config["LOCALISATION_DICT"] = eval(tags.read())
db = SQLAlchemy(app)


from statstool_web import routes
