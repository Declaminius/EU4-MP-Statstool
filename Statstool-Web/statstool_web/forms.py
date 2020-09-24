from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField, StringField, TextAreaField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from statstool_web.models import User

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

class RegistrationForm(FlaskForm):
    username = StringField("Username",
    validators = [DataRequired(), Length(min = 2, max = 20)])
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    confirm_password = PasswordField("Confirm Password",
    validators = [DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("Username taken.")

    def validate_email(self, email):
        email = User.query.filter_by(email = email.data).first()
        if email:
            raise ValidationError("Email already exists.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")
