from flask import render_template, url_for, send_from_directory, request, redirect, flash
from statstool_web.forms import SavegameSelectForm, TagSetupForm
from statstool_web import app, db
from statstool_web.parserfunctions import edit_parse
from statstool_web.models import Savegame
from werkzeug.utils import secure_filename
import os
import secrets

@app.route("/", methods = ["GET", "POST"])
@app.route("/home", methods = ["GET", "POST"])
def home():
    form = SavegameSelectForm()
    if form.validate_on_submit():
        savegame_ids = []
        for file in (request.files[form.savegame1.name],request.files[form.savegame2.name]):
            random = secrets.token_hex(8)
            path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], random)
            file.save(path)
            try:
                playertags, tag_list = edit_parse(path)
                savegame = Savegame(playertags = playertags, tag_list = tag_list, file = random)
                db.session.add(savegame)
                db.session.commit()
                savegame_ids.append(savegame.id)
            except AttributeError:
                pass
            except (IndexError, UnicodeDecodeError) as e:
                print(e)

        flash(f'Configure the nation tags you want to analyze.', 'success')
        return redirect(url_for("setup", savegame_ids = savegame_ids))
    return render_template("home.html", form = form)

@app.route("/setup/<savegame_ids>", methods = ["GET", "POST"])
def setup(savegame_ids):
    form = TagSetupForm()
    playertags = Savegame.query.get(savegame_ids[1]).playertags
    tag_list = Savegame.query.get(savegame_ids[1]).tag_list
    form.remove.choices = playertags
    form.add.choices = [tag for tag in tag_list if tag not in playertags]
    if request.method == "GET":
        return render_template("setup.html", form = form, playertags = sorted(playertags))
    if request.method == "POST":
        print(form.remove.data)
