from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField, StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class SavegameSelectForm(FlaskForm):
    savegame1 = FileField("Select first savegame", validators = [DataRequired(), FileAllowed(['eu4'], "Only EU4-Saves")])
    savegame2 = FileField("Select second savegame", validators = [DataRequired(), FileAllowed(['eu4'], "Only EU4-Saves")])
    submit = SubmitField("Parse")

class TagSetupForm(FlaskForm):
    remove = SelectField("Remove Nation")
    add = SelectField("Add Nation")
    submit = SubmitField("Parse")
    remove_button = SubmitField("Remove Nation")
    add_button = SubmitField("Add Nation")
