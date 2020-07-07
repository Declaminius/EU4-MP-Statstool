from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import DataRequired, Length

class SavegameForm(FlaskForm):
    name = StringField("Name", validators = [DataRequired(), Length(min = 2, max = 20)])
    savegame1 = FileField("Select first savegame", validators = [DataRequired(), FileAllowed(['png'], "Only EU4-Saves")])
    savegame2 = FileField("Select second savegame", validators = [DataRequired(), FileAllowed(['eu4'], "Only EU4-Saves")])
    submit = SubmitField("Parse")
