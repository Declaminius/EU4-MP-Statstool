from flask import render_template, url_for, send_from_directory, request, redirect, flash
from statstool_web.forms import SavegameSelectForm, TagSetupForm, NewNationForm
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
        sg_ids = []
        for file in (request.files[form.savegame1.name],request.files[form.savegame2.name]):
            random = secrets.token_hex(8)
            path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], random)
            file.save(path)
            try:
                playertags, tag_list = edit_parse(path)
                savegame = Savegame(file = random)
                for tag in tag_list:
                    savegame.nations.append(Nation.get(tag))
                    if tag in playertags:
                        savegame.playernations.append(Nation.get(tag))
                db.session.add(savegame)
                db.session.commit()
                sg_ids.append(savegame.id)
            except AttributeError:
                pass
            except (IndexError, UnicodeDecodeError) as e:
                print(e)
        flash(f'Configure the nation tags you want to analyze.', 'success')
        return redirect(url_for("setup", sg_id1 = sg_ids[0], sg_id2 = sg_ids[1]))
    return render_template("home.html", form = form)

@app.route("/setup/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
def setup(sg_id1,sg_id2):
    form = TagSetupForm()
    playertags = sorted([(tag,app.config["LOCALISATION_DICT"][tag]) \
    if tag in app.config["LOCALISATION_DICT"].keys() else (tag,tag) \
    for tag in set(Savegame.query.get(sg_id1).playertags + Savegame.query.get(sg_id2).playertags)], key = lambda x: x[1])
    if request.method == "GET":
        return render_template("setup.html", form = form, playertags = playertags,\
                sg_id1 = sg_id1, sg_id2 = sg_id2)
    if request.method == "POST":
        print("juhu")
        return redirect(url_for("main", sg_id1 = sg_id1, sg_id2 = sg_id2))

@app.route("/setup/new_nation/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
def new_nation(sg_id1,sg_id2):
    form = NewNationForm()
    new_tag_list = [tag for tag in Savegame.query.get(sg_id2).tag_list \
            if tag not in Savegame.query.get(sg_id2).playertags]
    form.select.choices = \
        sorted([(tag,app.config["LOCALISATION_DICT"][tag]) \
        if tag in app.config["LOCALISATION_DICT"].keys() else (tag,tag) \
        for tag in new_tag_list], key = lambda x: x[1])
    if request.method == "POST":
        sg = Savegame.query.get(sg_id2)
        if form.select.data not in sg.playertags:
            sg.playertags = sg.playertags + [form.select.data]
        db.session.commit()
        return redirect(url_for("setup", sg_id1 = sg_id1, sg_id2 = sg_id2))
    return render_template("new_nation.html", form = form)

@app.route("/setup/remove_nation/<int:sg_id1>/<int:sg_id2>/<string:tag>", methods = ["GET", "POST"])
def remove_nation(sg_id1,sg_id2,tag):
    for id in (sg_id1,sg_id2):
        sg = Savegame.query.get(id)
        if tag in sg.playertags:
            sg.playertags = [t for t in sg.playertags if t != tag]
            db.session.commit()
    return redirect(url_for("setup", sg_id1 = sg_id1, sg_id2 = sg_id2))

@app.route("/setup/remove_all/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
def remove_all(sg_id1,sg_id2):
    for id in (sg_id1,sg_id2):
        sg = Savegame.query.get(id)
        sg.playertags = []
        db.session.commit()
    return redirect(url_for("setup", sg_id1 = sg_id1, sg_id2 = sg_id2))

@app.route("/main/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
def main(sg_id1,sg_id2):
    for id in (sg_id1,sg_id2):
        savegame = Savegame.query.get(id)
        # savegame.stats_dict, savegame.year, savegame.total_trade_goods, savegame.sorted_tag_list,\
        # savegame.income_dict, savegame.color_dict,\
        # savegame.army_battle_list, savegame.navy_battle_list, savegame.province_stats_list,\
        # savegame.trade_stats_list, savegame.subject_dict,\
        # savegame.hre_reformlevel, savegame.trade_port_dict, savegame.war_list,\
        # savegame.war_dict, savegame.tech_dict, savegame.monarch_list, self.localisation_dict =\
        # parse(savegame.file, savegame.playertags, self.formable_nations_dict, self.pbar, self.plabel)
    return render_template("main.html")
