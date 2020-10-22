from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class NationFormationForm(FlaskForm):
    old_nation = SelectField("Old Nation")
    new_nation = SelectField("New Nation")
    submit = SubmitField("Confirm")
