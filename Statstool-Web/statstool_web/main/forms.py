from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import FileField, SubmitField, StringField, PasswordField, BooleanField, TextField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from statstool_web.models import User


class SavegameSelectForm(FlaskForm):
    savegame1 = FileField("Select first savegame", validators = [DataRequired(), FileAllowed(['eu4'], "Only EU4-Saves")])
    savegame1_name = StringField("First save name (optional)")
    savegame1_map = FileField("Upload first map (optional)", validators = [FileAllowed(['png', 'jpg'])])
    savegame2 = FileField("Select second savegame", validators = [DataRequired(), FileAllowed(['eu4'], "Only EU4-Saves")])
    savegame2_name = StringField("Second save name (optional)")
    savegame2_map = FileField("Upload second map (optional)", validators = [FileAllowed(['png', 'jpg'])])
    submit = SubmitField("Upload")

class OneSavegameSelectForm(FlaskForm):
    savegame = FileField("Select savegame", validators = [DataRequired(), FileAllowed(['eu4'], "Only EU4-Saves")])
    savegame_name = StringField("Save name (optional)")
    map = FileField("Upload map (optional)", validators = [FileAllowed(['png', 'jpg'])])
    submit = SubmitField("Upload")

class MapSelectForm(FlaskForm):
    map = FileField("Upload map", validators = [DataRequired(), FileAllowed(['png', 'jpg'])])
    submit = SubmitField("Upload")

class LoginForm(FlaskForm):
    username = StringField("Username",
    validators = [DataRequired(), Length(min = 2, max = 20)])
    password = PasswordField("Password", validators = [DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


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


class MPForm(FlaskForm):
    mp_name = StringField("MP-Name", validators = [DataRequired(), Length(min = 2, max = 100)])
    mp_description = TextField("Beschreibung")
    gm = StringField("Spielleiter")
    host = StringField("Host")
    checksum = StringField("Checksumme", validators = [Length(min = 4, max = 4)])
    next_gameday = StringField("Nächster Spieltag")
    institutions = BooleanField("Institutionen")
    victory_points = BooleanField("Siegpunkte")
    teams_setting = BooleanField("Teams")
    submit = SubmitField("Save Changes")


class ConfigureTeamsForm(FlaskForm):
    submit = SubmitField("Back")

class NewTeamForm(FlaskForm):
    id = IntegerField("Team-ID")
    select1 = StringField("Add First Nation")
    select2 = StringField("Add Second Nation")
    submit = SubmitField("Confirm")


class EditVPForm(FlaskForm):
    first_player_war = BooleanField("Erster Spielerkrieg-Sieger")
    global_trade_spawn = BooleanField("Globaler Handel")
    submit = SubmitField("Confirm")
