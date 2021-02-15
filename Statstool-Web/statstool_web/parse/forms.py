from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class TagSetupForm0(FlaskForm):
    submit = SubmitField("Parse Part 1")

class TagSetupForm1(FlaskForm):
    submit = SubmitField("Parse Part 2")

class NewNationForm(FlaskForm):
    select = SelectField("Add Nation")
    submit = SubmitField("Confirm")
