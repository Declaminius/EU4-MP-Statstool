from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from statstool_web.config import Config
from .util import ListConverter
from flask_sqlalchemy import models_committed

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "info"
db = SQLAlchemy()


def create_app(config_class = Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    app.url_map.converters['list'] = ListConverter
    with open("files/tags.txt", "r", encoding = 'utf-8') as tags:
        app.config["LOCALISATION_DICT"] = eval(tags.read())

    @models_committed.connect_via(app)
    def on_models_committed(sender, changes):
        for obj, change in changes:
            if change == 'delete' and hasattr(obj, '__commit_delete__'):
                obj.__commit_delete__()

    from statstool_web.main.routes import main
    from statstool_web.parse.routes import parse
    from statstool_web.show_stats.routes import show_stats

    app.register_blueprint(main)
    app.register_blueprint(parse)
    app.register_blueprint(show_stats)

    return app
