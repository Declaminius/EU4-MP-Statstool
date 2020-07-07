from flask import Flask, render_template, url_for
from forms import SavegameForm
from flask_sqlalchemy import SQLAlchemy
from parserfunctions import edit_parse

app = Flask(__name__)
app.config["SECRET_KEY"] = '8e32962d3ed1bc103e804b9136281acd'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class Savegame(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    playertags = db.Column(db.PickleType, nullable = False)
    tag_list = db.Column(db.PickleType, nullable = False)
    file = db.Column(db.String(120), nullable = False)

@app.route("/", methods = ["GET", "POST"])
@app.route("/home", methods = ["GET", "POST"])
def home():
    form = SavegameForm()
    print("FormErrors:", form.errors)
    print("NameErrors:", form.name.errors)
    if form.validate_on_submit():
        print(form.savegame1.data)
        print(form.savegame1.errors)
        print("Valide")
        try:
            savegame1 = Savegame(*edit_parse(form.savegame1.data),form.savegame1.data.split("/")[-1])
            savegame2 = Savegame(*edit_parse(form.savegame2.data),form.savegame2.data.split("/")[-1])
        except AttributeError:
            pass
        except (IndexError, UnicodeDecodeError) as e:
            print(e)
		# try:
		# 	savegame = Savegame(self.playertags, self.tag_list, self.FILEDIR)
		# 	savegame.directory = "C:/Users/kunde/Desktop/{}-images".format(self.FILENAME.split(".")[0])
		# 	if sender.text() == "Savegame 1":
		# 		self.savegame_list[0] = savegame
		# 	if sender.text() == "Savegame 2":
		# 		self.savegame_list[1] = savegame
		# except (NameError, AttributeError):
		# 	pass
		# if self.savegame_list[0] and self.savegame_list[1]:
		# 	self.parse_button.setEnabled(True)
        db.session.add(savegame1)
        db.session.add(savegame2)
        db.session.commit()
        flash(f'Configure the nation tags you want to analyze.', 'success')
        return render_template("layout.html", savegame1 = savegame1, savegame2 = savegame2)
    return render_template("home.html", form = form)



if __name__ == '__main__':
    app.run(debug=True)
