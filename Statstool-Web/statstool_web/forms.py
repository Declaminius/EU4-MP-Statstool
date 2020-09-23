from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField, StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class SavegameSelectForm(FlaskForm):
    savegame1 = FileField("Select first savegame", validators = [DataRequired(), FileAllowed(['eu4'], "Only EU4-Saves")])
    savegame1_map = FileField("Upload first map (optional)", validators = [FileAllowed(['png', 'jpg'])])
    savegame2 = FileField("Select second savegame", validators = [DataRequired(), FileAllowed(['eu4'], "Only EU4-Saves")])
    savegame2_map = FileField("Upload second map (optional)", validators = [FileAllowed(['png', 'jpg'])])
    submit = SubmitField("Parse")

class OneSavegameSelectForm(FlaskForm):
    savegame = FileField("Select savegame", validators = [DataRequired(), FileAllowed(['eu4'], "Only EU4-Saves")])
    map = FileField("Upload map (optional)", validators = [FileAllowed(['png', 'jpg'])])
    submit = SubmitField("Parse")

class MapSelectForm(FlaskForm):
    map = FileField("Upload map", validators = [DataRequired(), FileAllowed(['png', 'jpg'])])
    submit = SubmitField("Parse")

class TagSetupForm(FlaskForm):
    submit = SubmitField("Parse")

class NewNationForm(FlaskForm):
    select = SelectField("Add Nation")
    submit = SubmitField("Confirm")

class NationFormationForm(FlaskForm):
    old_nation = SelectField("Old Nation")
    new_nation = SelectField("New Nation")
    submit = SubmitField("Confirm")
