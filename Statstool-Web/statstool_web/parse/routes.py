from flask import render_template, url_for, request, redirect, flash, Blueprint, current_app
from statstool_web.parse.forms import *
from statstool_web import db
from statstool_web.models import Savegame, NationFormation, Nation, NationSavegameData
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_required

import os

parse = Blueprint('parse', __name__)

@parse.route("/setup/<int:sg_id1>/<int:sg_id2>/<int:part>", methods = ["GET", "POST"])
@login_required
def setup(sg_id1,sg_id2, part):
    if part == 0:
        form = TagSetupForm0()
    elif part == 1:
        form = TagSetupForm1()
    old_savegame = Savegame.query.get(sg_id1)
    new_savegame = Savegame.query.get(sg_id2)
    nations = new_savegame.player_nations
    names_dict = {}
    for nation in nations:
        nation_data =  NationSavegameData.query.filter_by(savegame_id = sg_id2, \
                                                nation_tag = nation.tag).first()
        if nation_data.player_name:
            names_dict[nation.tag] = nation_data.player_name
        else:
            names_dict[nation.tag] = "???"

    playertags =  sorted([(nation.tag,current_app.config["LOCALISATION_DICT"][nation.tag], names_dict[nation.tag]) \
        if nation.tag in current_app.config["LOCALISATION_DICT"].keys() else (nation.tag,nation.tag, names_dict[nation.tag]) \
        for nation in nations], key = lambda x: x[1])
    if request.method == "GET":
        return render_template("parse/setup.html", form = form, playertags = playertags,\
                sg_id1 = sg_id1, sg_id2 = sg_id2)
    if request.method == "POST":
        if sg_id1 != sg_id2:
            old_tag_list = [nation.tag for nation in old_savegame.player_nations]
            new_tag_list = [nation.tag for nation in new_savegame.player_nations]
            for tag in new_tag_list:
                if tag in old_tag_list:
                    formation = NationFormation(old_savegame_id = sg_id1, new_savegame_id = sg_id2, old_nation_tag = tag, new_nation_tag = tag)
                    db.session.add(formation)
                elif tag in [nation.tag for nation in old_savegame.nations]:
                    old_savegame.player_nations.append(Nation.query.get(tag))
                    formation = NationFormation(old_savegame_id = sg_id1, new_savegame_id = sg_id2, old_nation_tag = tag, new_nation_tag = tag)
                    db.session.add(formation)
            try:
                db.session.flush()
            except IntegrityError:
                db.session.rollback()
            else:
                db.session.commit()
        return redirect(url_for("show_stats.parse", sg_id1 = sg_id1, sg_id2 = sg_id2, part = part))

@parse.route("/setup/new_nation/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
@login_required
def new_nation(sg_id1,sg_id2):
    form = NewNationForm()
    playertags = [nation.tag for nation in Savegame.query.get(sg_id2).player_nations]
    tag_list = [nation.tag for nation in Savegame.query.get(sg_id2).nations \
                if nation.tag not in playertags]
    form.select.choices = \
        sorted([(tag,current_app.config["LOCALISATION_DICT"][tag]) \
        if tag in current_app.config["LOCALISATION_DICT"].keys() else (tag,tag) \
        for tag in tag_list], key = lambda x: x[1])
    if request.method == "POST":
        sg = Savegame.query.get(sg_id2)
        if form.select.data not in sg.player_nations:
            sg.player_nations.append(Nation.query.get(form.select.data))
        db.session.commit()
        return redirect(url_for("parse.setup", sg_id1 = sg_id1, sg_id2 = sg_id2, part = 0))
    return render_template("parse/new_nation.html", form = form)

@parse.route("/setup/all_nations/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
@login_required
def all_nations(sg_id1,sg_id2):
    sg = Savegame.query.get(sg_id2)
    for nation in sg.nations:
        if nation not in sg.player_nations:
            sg.player_nations.append(nation)
    db.session.commit()
    return redirect(url_for("parse.setup", sg_id1 = sg_id1, sg_id2 = sg_id2, part = 0))

@parse.route("/setup/remove_nation/<int:sg_id1>/<int:sg_id2>/<string:tag>", methods = ["GET", "POST"])
@login_required
def remove_nation(sg_id1, tag, sg_id2):
    if sg_id2:
        ids = [sg_id1,sg_id2]
    else:
        ids = [sg_id1]
    for id in ids:
        sg = Savegame.query.get(id)
        playertags = [nation.tag for nation in sg.player_nations]
        if tag in playertags:
            sg.player_nations.remove(Nation.query.get(tag))
            db.session.commit()
    return redirect(url_for("parse.setup", sg_id1 = sg_id1, sg_id2 = sg_id2, part = 0))

@parse.route("/setup/remove_all/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
@login_required
def remove_all(sg_id1,sg_id2):

    for id in (sg_id1,sg_id2):
        sg = Savegame.query.get(id)
        sg.player_nations = []
        db.session.commit()
    return redirect(url_for("parse.setup", sg_id1 = sg_id1, sg_id2 = sg_id2, part = 0))
