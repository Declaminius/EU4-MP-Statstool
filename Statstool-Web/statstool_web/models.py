from statstool_web import db


class Savegame(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    playertags = db.Column(db.PickleType, nullable = False)
    tag_list = db.Column(db.PickleType, nullable = False)
    file = db.Column(db.String(120), nullable = False)
