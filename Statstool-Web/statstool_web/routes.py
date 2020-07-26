from flask import render_template, url_for, send_from_directory, request, redirect, flash
from statstool_web.forms import SavegameSelectForm, TagSetupForm, NewNationForm
from statstool_web import app, db
from statstool_web.parserfunctions import edit_parse, parse
from statstool_web.models import Savegame, Nation, NationSavegameData
from werkzeug.utils import secure_filename
import os
import secrets
from pathlib import Path
from sqlalchemy.orm import load_only

@app.route("/", methods = ["GET", "POST"])
@app.route("/home", methods = ["GET", "POST"])
def home():
    form = SavegameSelectForm()
    if form.validate_on_submit():
        sg_ids = []
        Path(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])).mkdir(parents=True, exist_ok=True)
        for file in (request.files[form.savegame1.name],request.files[form.savegame2.name]):
            random = secrets.token_hex(8) + ".eu4"
            path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], random)
            file.save(path)
            try:
                playertags, tag_list = edit_parse(path)
                savegame = Savegame(file = path)
                for tag in tag_list:
                    if not Nation.query.get(tag):
                        if tag in app.config["LOCALISATION_DICT"].keys():
                            t = Nation(tag = tag, name = app.config["LOCALISATION_DICT"][tag])
                        else:
                            t = Nation(tag = tag, name = tag)
                        db.session.add(t)
                        db.session.commit()

                    savegame.nations.append(Nation.query.get(tag))
                    if tag in playertags:
                        savegame.player_nations.append(Nation.query.get(tag))

                db.session.add(savegame)
                db.session.commit()
                sg_ids.append(savegame.id)
            except AttributeError as e:
                print(e)
            except (IndexError, UnicodeDecodeError) as e:
                print(e)
        flash(f'Configure the nation tags you want to analyze.', 'success')
        return redirect(url_for("setup", sg_id1 = sg_ids[0], sg_id2 = sg_ids[1]))
    return render_template("home.html", form = form)

@app.route("/setup/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
def setup(sg_id1,sg_id2):
    form = TagSetupForm()
    playertags = sorted([(nation.tag,app.config["LOCALISATION_DICT"][nation.tag]) \
    if nation.tag in app.config["LOCALISATION_DICT"].keys() else (nation.tag,nation.tag) \
    for nation in set(Savegame.query.get(sg_id1).player_nations + Savegame.query.get(sg_id2).player_nations)], key = lambda x: x[1])
    if request.method == "GET":
        return render_template("setup.html", form = form, playertags = playertags,\
                sg_id1 = sg_id1, sg_id2 = sg_id2)
    if request.method == "POST":
        return redirect(url_for("main", sg_id1 = sg_id1, sg_id2 = sg_id2))

@app.route("/setup/new_nation/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
def new_nation(sg_id1,sg_id2):
    form = NewNationForm()
    playertags = [nation.tag for nation in Savegame.query.get(sg_id2).player_nations]
    new_tag_list = [nation.tag for nation in Savegame.query.get(sg_id2).nations \
            if nation.tag not in playertags]
    form.select.choices = \
        sorted([(tag,app.config["LOCALISATION_DICT"][tag]) \
        if tag in app.config["LOCALISATION_DICT"].keys() else (tag,tag) \
        for tag in new_tag_list], key = lambda x: x[1])
    if request.method == "POST":
        sg = Savegame.query.get(sg_id2)
        if form.select.data not in sg.player_nations:
            sg.player_nations.append(Nation.query.get(form.select.data))
        db.session.commit()
        return redirect(url_for("setup", sg_id1 = sg_id1, sg_id2 = sg_id2))
    return render_template("new_nation.html", form = form)

@app.route("/setup/remove_nation/<int:sg_id1>/<int:sg_id2>/<string:tag>", methods = ["GET", "POST"])
def remove_nation(sg_id1,sg_id2,tag):
    for id in (sg_id1,sg_id2):
        sg = Savegame.query.get(id)
        playertags = [nation.tag for nation in sg.player_nations]
        if tag in playertags:
            sg.player_nations.remove(Nation.query.get(tag))
            db.session.commit()
    return redirect(url_for("setup", sg_id1 = sg_id1, sg_id2 = sg_id2))

@app.route("/setup/remove_all/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
def remove_all(sg_id1,sg_id2):
    for id in (sg_id1,sg_id2):
        sg = Savegame.query.get(id)
        sg.player_nations = []
        db.session.commit()
    return redirect(url_for("setup", sg_id1 = sg_id1, sg_id2 = sg_id2))

@app.route("/main/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
def main(sg_id1,sg_id2):
    for id in (sg_id1,sg_id2):
        savegame = Savegame.query.get(id)
        parse(savegame)
        db.session.commit()
    return render_template("main.html", sg_id1 = sg_id1, sg_id2 = sg_id2)

@app.route("/overview_table/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
def overview_table(sg_id1,sg_id2):
    random = secrets.token_hex(8) + ".json"
    path = os.path.join(app.root_path, 'json', random)
    columns = ["nation_tag", "adm_tech", "dip_tech", "mil_tech"]
    nation_data = []
    for nation in Savegame.query.get(sg_id).player_nations:
        data = NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id).with_entities(*columns).first()._asdict()
        nation_data.append(data)
    return render_template("overview_table.html", data = nation_data, columns = columns)

@app.route("/main/<int:sg_id>/test", methods = ["GET", "POST"])
def test(sg_id):
    return render_template("test.html")
