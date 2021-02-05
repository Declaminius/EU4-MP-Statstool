import os

class Config():
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOAD_FOLDER = 'static/savegames'
    ADMIN_NAME = os.environ.get("ADMIN_NAME")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
