from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class TagSetupForm(FlaskForm):
    submit = SubmitField("Parse")

class NewNationForm(FlaskForm):
    select = SelectField("Add Nation")
    submit = SubmitField("Confirm")
