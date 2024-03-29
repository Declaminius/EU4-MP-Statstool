from flask import render_template, url_for, request, redirect, flash, abort, Blueprint, current_app
from statstool_web.show_stats.forms import NationFormationForm
from statstool_web.show_stats.util import *
from statstool_web.show_stats.outsource import *
from statstool_web import db, bcrypt
from statstool_web.models import *
from statstool_web.util import redirect_url
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_required
import statstool_web.parserfunctions
from colour import Color

import os
import secrets
import matplotlib
import matplotlib.pyplot as plt

show_stats = Blueprint('show_stats', __name__)

matplotlib.use('Agg')

@show_stats.route("/parse/<int:sg_id1>/<int:sg_id2>/<int:part>", methods = ["GET"])
def parse(sg_id1,sg_id2, part):
    for id in (sg_id1,sg_id2):
        savegame = Savegame.query.get(id)
        if part == 0 and not savegame.parse_flag0:
            statstool_web.parserfunctions.parse_part0(savegame)
        elif part == 1 and not savegame.parse_flag:
            statstool_web.parserfunctions.parse_part1(savegame)
        if savegame.parse_flag:
            try:
                os.remove(os.path.join(current_app.root_path, current_app.config["UPLOAD_FOLDER"], savegame.file))
            except FileNotFoundError:
                pass

    old_savegame = Savegame.query.get(sg_id1)
    new_savegame = Savegame.query.get(sg_id2)
    if sg_id1 != sg_id2:
        for nation in new_savegame.player_nations:
            if nation in old_savegame.player_nations:
                if NationFormation.query.get((sg_id1,sg_id2,nation.tag,nation.tag)) is None:
                    formation = NationFormation(old_savegame_id = sg_id1, new_savegame_id = sg_id2, old_nation_tag = nation.tag, new_nation_tag = nation.tag)
                    db.session.add(formation)
    db.session.commit()
    if not savegame.parse_flag:
        return(redirect(url_for("parse.setup", sg_id1 = sg_id1, sg_id2 = sg_id2, part = 1)))
    else:
        if current_user.is_authenticated and sg_id1 != sg_id2:
            return redirect(url_for("show_stats.configure", sg_id1 = sg_id1, sg_id2 = sg_id2))
        else:
            return redirect(url_for("show_stats.overview_table", sg_id1 = sg_id1, sg_id2 = sg_id2))

@show_stats.route("/map/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def map(sg_id1,sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    return render_template("show_stats/show_stats_layout.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), mp = mp)

@show_stats.route("/remove_nation_formation/<int:sg_id1>/<int:sg_id2>/<string:old>/<string:new>", methods = ["GET", "POST"])
def remove_nation_formation(sg_id1,sg_id2,old,new):
    formation = NationFormation.query.get((sg_id1,sg_id2,old,new))
    db.session.delete(formation)
    db.session.commit()
    return redirect(url_for("show_stats.configure", sg_id1 = sg_id1, sg_id2 = sg_id2))

@show_stats.route("/configure/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
@login_required
def configure(sg_id1,sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    form = NationFormationForm()
    if request.method == "POST":
        formation = NationFormation(old_savegame_id = sg_id1, new_savegame_id = sg_id2, old_nation_tag = form.old_nation.data, new_nation_tag = form.new_nation.data)
        db.session.add(formation)
        try:
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
        else:
            db.session.commit()

    old_savegame = Savegame.query.get(sg_id1)
    new_savegame = Savegame.query.get(sg_id2)

    old_matching_tags = [x.old_nation_tag for x in NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2).all()]
    new_matching_tags = [x.new_nation_tag for x in NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2).all()]
    old_tag_list = [nation.tag for nation in old_savegame.player_nations if nation.tag not in old_matching_tags]
    new_tag_list = [nation.tag for nation in new_savegame.player_nations if nation.tag not in new_matching_tags]


    for field, tag_list, sg_id in ((form.old_nation,old_tag_list, sg_id1), (form.new_nation,new_tag_list, sg_id2)):
        field.choices = \
            sorted([(tag,NationSavegameData.query.filter_by(savegame_id = sg_id, \
            nation_tag = tag).first().nation_name) for tag in tag_list], key = lambda x: x[1])

    nation_formations = []
    for x in NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2).all():
        old_nation = NationSavegameData.query.filter_by(savegame_id = sg_id1, nation_tag = x.old_nation_tag).first()
        new_nation = NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = x.new_nation_tag).first()
        nation_formations.append((old_nation, new_nation))
    return render_template("show_stats/configure.html", old_savegame = old_savegame, new_savegame = new_savegame, \
            form = form, nation_formations = nation_formations, mp = mp)

@show_stats.route("/overview_table/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def overview_table(sg_id1,sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    columns = ["great_power_score", "development", "effective_development", "navy_strength", "max_manpower", "income"]
    header_labels = ["Nation", "Great Power Score", "Development", "Effective Development", "Navy Strength", "Maximum Manpower", "Monthly Income"]
    nation_data = []
    nation_colors_hex = []
    nation_colors_hsl = []
    nation_names = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        data = NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).with_entities(*columns).first()._asdict()
        for column in data.keys():
            data[column] = round(data[column], 3)
        nation_data.append(data)
        nation_colors_hex.append( NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first().color)
        nation_colors_hsl.append( NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first().color.hsl)
        nation_names.append(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).first().nation_name)
    return render_template("show_stats/table.html", old_savegame = Savegame.query.get(sg_id1), \
            new_savegame = Savegame.query.get(sg_id2), data = zip(nation_data,nation_names,nation_colors_hex, nation_colors_hsl), \
            columns = columns, header_labels = header_labels, colorize_columns = [1,2,3,4,5,6], sort_by = 1, map = map, mp = mp)

@show_stats.route("/overview_table_teams/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def overview_table_teams(sg_id1,sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    columns = ["great_power_score", "development",  "effective_development", "navy_strength", "max_manpower", "income"]
    header_labels = ["Team", "Great Power Score", "Development", "Effective Development", "Navy Strength", "Maximum Manpower", "Monthly Income"]
    teams = mp.teams
    team_names = ["Team {}".format(team.id) for team in teams]
    team_ids = [team.id for team in teams]
    team_colors_hex = ["#ffffff"]*len(teams)
    team_colors_hsl = [(0,0,100)]*len(teams)

    team_data = []
    for team in teams:
        team_tags = (team.team_tag1, team.team_tag2)
        data = dict(zip(columns, [0 for x in range(len(columns))]))

        for tag in team_tags:
            result = NationSavegameData.query.filter_by(nation_tag = tag, \
                savegame_id = sg_id2).first().__dict__
            for column in columns:
                data[column] += result[column]
                data[column] = round(data[column], 3)
        team_data.append(data)
    return render_template("show_stats/table.html", old_savegame = Savegame.query.get(sg_id1), \
            new_savegame = Savegame.query.get(sg_id2), data = zip(team_data,team_names,team_colors_hex, team_colors_hsl), \
            columns = columns, header_labels = header_labels, colorize_columns = [1,2,3,4,5,6], sort_by = 1, map = map, mp = mp)

@show_stats.route("/development/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def development(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(["development"], \
            [NationSavegameData.development], NationSavegameData, sg_id1, sg_id2)
    return render_template("show_stats/plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, ids = ids, \
            header_labels = header_labels, columns = columns, map = map, mp = mp)

@show_stats.route("/effective_development/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def effective_development(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(["effective_development"], \
            [NationSavegameData.effective_development], NationSavegameData, sg_id1, sg_id2)
    return render_template("show_stats/plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, ids = ids, \
            header_labels = header_labels, columns = columns, map = map, mp = mp)

@show_stats.route("/income/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def income(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(["income"], [NationSavegameData.income], NationSavegameData, sg_id1, sg_id2)

    return render_template("show_stats/plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, \
            ids = ids, header_labels = header_labels, columns = columns, map = map, mp = mp)

@show_stats.route("/max_manpower/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def max_manpower(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    content, ids, header_labels, columns, flattened_image_files, map = \
        get_images_and_table_data(["max_manpower"], [NationSavegameData.max_manpower], NationSavegameData, sg_id1, sg_id2)

    return render_template("show_stats/plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, \
            ids = ids, header_labels = header_labels, columns = columns, map = map, mp = mp)

@show_stats.route("/tech/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def tech(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    
    columns = ["adm_tech", "dip_tech", "mil_tech", "number_of_ideas", "innovativeness"]

    header_labels = ["Nation", "ADM", "DIP", "MIL", "Ideen", "Innovativität"]

    nation_data = []
    nation_colors_hex = []
    nation_colors_hsl = []
    nation_names = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        data = NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).with_entities(*columns).first()._asdict()
        for column in data.keys():
            data[column] = round(data[column], 3)
        nation_data.append(data)
        nation_colors_hex.append( NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first().color)
        nation_colors_hsl.append( NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first().color.hsl)
        nation_names.append(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).first().nation_name)



    return render_template("show_stats/table.html", old_savegame = Savegame.query.get(sg_id1), \
            new_savegame = Savegame.query.get(sg_id2), data = zip(nation_data,nation_names,nation_colors_hex, nation_colors_hsl), \
            columns = columns, header_labels = header_labels, colorize_columns = [1,2,3,4,5,], sort_by = 5, map = map, mp = mp)

@show_stats.route("/army_losses_total/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def army_losses_total(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    categories = ["total"]
    columns = [NationSavegameArmyLosses.total]

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(categories, columns, NationSavegameArmyLosses, sg_id1, sg_id2)

    return render_template("show_stats/plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, \
            ids = ids, header_labels = header_labels, columns = columns, map = map, mp = mp)

@show_stats.route("/army_losses_infantry/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def army_losses_infantry(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    categories = ["infantry"]
    columns = [NationSavegameArmyLosses.infantry]

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(categories, columns, NationSavegameArmyLosses, sg_id1, sg_id2)

    return render_template("show_stats/plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, \
            ids = ids, header_labels = header_labels, columns = columns, map = map, mp = mp)

@show_stats.route("/army_losses_cavalry/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def army_losses_cavalry(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    categories = ["cavalry"]
    columns = [NationSavegameArmyLosses.cavalry]

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(categories, columns, NationSavegameArmyLosses, sg_id1, sg_id2)

    return render_template("show_stats/plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, \
            ids = ids, header_labels = header_labels, columns = columns, map = map, mp = mp)

@show_stats.route("/army_losses_artillery/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def army_losses_artillery(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    categories = ["artillery"]
    columns = [NationSavegameArmyLosses.artillery]

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(categories, columns, NationSavegameArmyLosses, sg_id1, sg_id2)

    return render_template("show_stats/plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, ids = ids, \
            header_labels = header_labels, columns = columns, map = map, mp = mp)

@show_stats.route("/army_losses_combat/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def army_losses_combat(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    categories = ["combat"]
    columns = [NationSavegameArmyLosses.combat]

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(categories, columns, NationSavegameArmyLosses, sg_id1, sg_id2)

    return render_template("show_stats/plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, \
            ids = ids, header_labels = header_labels, columns = columns, map = map, mp = mp)

@show_stats.route("/army_losses_attrition/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def army_losses_attrition(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    categories = ["attrition"]
    columns = [NationSavegameArmyLosses.attrition]

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(categories, columns, NationSavegameArmyLosses, sg_id1, sg_id2)

    return render_template("show_stats/plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, ids = ids, \
            header_labels = header_labels, columns = columns, map = map, mp = mp)

@show_stats.route("/income_over_time/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def income_over_time(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    new_year = Savegame.query.get(sg_id2).year
    image_files = []
    for (old_year, category) in zip((1445,Savegame.query.get(sg_id1).year),("income_over_time_total","income_over_time_latest")):
        income_plot(category, old_year, new_year, sg_id1, sg_id2)
        image_files.append(SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = category).first().filename)
    map = Savegame.query.get(sg_id2).map_file
    return render_template("show_stats/income_plot.html", old_savegame = Savegame.query.get(sg_id1), \
            new_savegame = Savegame.query.get(sg_id2), image_files = image_files, \
            map = map, mp = mp)

@show_stats.route("/provinces/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def provinces(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    columns = ["province_id", "base_tax", "base_production", "base_manpower", "development", "trade_power", "religion", "culture"]
    header_labels = ["Nation", "ID", "Name", "Steuer", "Produktion", "Mannstärke", "Entwicklung", "Handelsmacht", "Religion", "Kultur", "Handelsgut"]
    province_data = []
    nation_colors = []
    nation_tags = []
    for province in NationSavegameProvinces.query.filter_by(savegame_id = sg_id2).all():
        province = province.__dict__
        data = {x: province[x] for x in columns}
        owner = NationSavegameData.query.filter_by(nation_tag = province["nation_tag"], \
                savegame_id = sg_id2).first()
        if owner:
            nation_colors.append(owner.color)
        else:
            nation_colors.append(Color("#ffffff"))
        nation_tags.append(province["nation_tag"])
        trade_good_name = TradeGood.query.filter_by(id = province["trade_good_id"]).first().name
        data["trade_good_name"] = trade_good_name
        province = Province.query.filter_by(id = province["province_id"]).first()
        data["name"] = province.name
        province_data.append(data)

    columns.append("trade_good_name")
    columns.insert(1, "name")
    return render_template("show_stats/province_table.html", old_savegame = Savegame.query.get(sg_id1), \
            new_savegame = Savegame.query.get(sg_id2), data = zip(province_data,nation_tags,nation_colors), \
            columns = columns, header_labels = header_labels, mp = mp)

@show_stats.route("/army_battles/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def army_battles(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    columns = ["date", "attacker_country", "attacker_infantry", "attacker_cavalry", \
        "attacker_artillery", "attacker_total", "attacker_losses", "attacker_commander", \
        "defender_country", "defender_infantry", "defender_cavalry", \
        "defender_artillery", "defender_total", "defender_losses", "defender_commander", "total_combatants", "total_losses"]
    header_labels = ["Datum", "Angreifer", "Inf", "Kav", "Art", "Gesamt", "Verluste", "General", \
        "Verteidiger", "Inf", "Kav", "Art", "Gesamt", "Verluste", "General", "Truppen", "Verluste"]
    battle_data = []
    nation_tags = []
    for battle in ArmyBattle.query.filter_by(savegame_id = sg_id2).all():
        battle = battle.__dict__
        data = {x: [battle[x],Color("#ffffff")] for x in columns}
        for column in ("attacker_country","defender_country"):
            nation = NationSavegameData.query.filter_by(nation_tag = data[column][0], savegame_id = sg_id2).first()
            if nation:
                data[column][1] = nation.color
        result = battle["result"]
        if result == "yes":
            data["attacker_commander"][1] = Color("green")
            data["defender_commander"][1] = Color("red")
        if result == "no":
            data["attacker_commander"][1] = Color("red")
            data["defender_commander"][1] = Color("green")
        battle_data.append(data)

    colorize_columns = [3,4,5,6,10,11,12,13,16]
    colorize_columns_rev = [7,14,17]
    return render_template("show_stats/army_battles_table.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
        data = battle_data, columns = columns, header_labels = header_labels, \
        colorize_columns = colorize_columns, colorize_columns_rev = colorize_columns_rev, \
        order_by = len(columns) - 1, mp = mp, title = "Schlachten")


@show_stats.route("/wars/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def wars(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    columns = ["name", "start_date", "infantry", "cavalry", "artillery", "combat", "attrition", "total", "ongoing"]
    header_labels = ["Name", "Startdatum", "Angreifer", "Verteidiger", "Infanterie", "Kavallerie", "Artillerie", "Kampf", "Zermürbung", "Gesamt", "Laufend"]
    war_data = []
    for war in War.query.filter_by(savegame_id = sg_id2).all():
        war_dict = war.__dict__
        data = {x: [war_dict[x],Color("#ffffff")] for x in columns}
        if war.attacker:
            if (nation_data := NationSavegameData.query.filter_by(nation_tag = war.attacker[0].tag, savegame_id = sg_id2).first()):
                if nation_data.nation_name:
                    data["attacker"] = [nation_data.nation_name, nation_data.color]
                else:
                    data["attacker"] = [war.attacker[0].tag, nation_data.color]
            else:
                data["attacker"] = [war.attacker[0].tag, Color("#ffffff")]
        else:
            data["attacker"] = ["", Color("#ffffff")]
        if war.defender:
            if (nation_data := NationSavegameData.query.filter_by(nation_tag = war.defender[0].tag, savegame_id = sg_id2).first()):
                if nation_data.nation_name:
                    data["defender"] = [nation_data.nation_name, nation_data.color]
                else:
                    data["defender"] = [war.defender[0].tag, nation_data.color]
            else:
                data["defender"] = [war.defender[0].tag, Color("#ffffff")]
        else:
            data["defender"] = ["", Color("#ffffff")]
        war_data.append(data)
    columns.insert(2, "attacker")
    columns.insert(3, "defender")
    return render_template("show_stats/army_battles_table.html", old_savegame = Savegame.query.get(sg_id1), \
        new_savegame = Savegame.query.get(sg_id2), data = war_data, columns = columns, \
        header_labels = header_labels, title = "Kriegsverluste", \
        colorize_columns = [], colorize_columns_rev = [i for i in range(5,len(header_labels))], \
        order_by = len(header_labels)-2, mp = mp)

@show_stats.route("/mana_spent_total/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def mana_spent_total(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    columns = ["adm", "dip", "mil", "total"]
    header_labels = ["Nation", "ADM", "DIP", "MIL", "Total"]
    data = mana_spent_table_total(header_labels, sg_id2)
    return render_template("show_stats/table.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            data = data, columns = columns, header_labels = header_labels, \
            colorize_columns = [i for i in range(1,len(header_labels))], \
            sort_by = len(header_labels) - 1, map = map, title = "Gesamt", mp = mp)

@show_stats.route("/mana_spent_ideas_tech_dev/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def mana_spent_ideas_tech_dev(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    columns = [0, 1, 7]
    header_labels = ["Nation", "Ideas", "%", "Technology", "%", "Development", "%", "Rest", "%", "Gesamt"]
    mana_data = []
    nation_names = []
    tag_list = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        tag_list.append(nation.tag)
        data = {}
        for id in columns:
            data[id] = 0
        mana = NationSavegamePointsSpent.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).all()
        if mana:
            data["total"] = sum([x.amount for x in mana])
            for id in columns:
                if (points_spent := NationSavegamePointsSpent.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag, points_spent_id = id).all()):
                    data[id] += sum([points.amount for points in points_spent])
                    data[str(id)] = round(data[id]/data["total"],2)
            data["rest"] = data["total"] - sum([data[id] for id in columns])
            data["p_rest"] = round(data["rest"]/data["total"],2)
        else:
            data["total"] = 0

        mana_data.append(data)
        nation_names.append(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).first().nation_name)

    map = Savegame.query.get(sg_id2).map_file
    columns = [0,"0",1,"1",7,"7","rest","p_rest","total"]
    nation_colors_hex, nation_colors_hsl = get_colors_hex_hsl(sg_id2, tag_list, NationSavegameData)
    return render_template("show_stats/table.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
        data = zip(mana_data,nation_names,nation_colors_hex, nation_colors_hsl), columns = columns, header_labels = header_labels, \
                colorize_columns = [i for i in range(1,len(header_labels))], \
                sort_by = len(header_labels) - 1, map = map, mp = mp)

@show_stats.route("/mana_spent_adm/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def mana_spent_adm(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    columns = [0,1,2,7,15,17]
    header_labels = ["Nation", "Ideas", "Tech", "Stability", "Development",\
    "Reduce Inflation", "Cores", "Sonstiges", "Gesamt"]
    data, columns = mana_spent_table("adm", columns, header_labels, sg_id2)
    return render_template("show_stats/table.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
        data = data, columns = columns, header_labels = header_labels, \
                colorize_columns = [i for i in range(1,len(header_labels))], \
                sort_by = len(header_labels) - 1, map = map, title = "ADM", mp = mp)

@show_stats.route("/mana_spent_dip/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def mana_spent_dip(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    columns = [0,1,7,14,20,22,34,46]
    header_labels = ["Country", "Ideas", "Tech","Development", "DipCost Peacedeal",\
    "Culture Conversions", "Reduce War Exhaustion",\
    "Promote Culture", "Admirals", "Sonstiges", "Gesamt"]
    data, columns = mana_spent_table("dip", columns, header_labels, sg_id2)
    return render_template("show_stats/table.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            data = data, columns = columns, header_labels = header_labels, \
            colorize_columns = [i for i in range(1,len(header_labels))], \
            sort_by = len(header_labels) - 1, map = map, title = "DIP", mp = mp)

@show_stats.route("/mana_spent_mil/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def mana_spent_mil(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp

    columns = [0,1,7,21,36,39,45,46]
    header_labels = ["Country", "Ideas", "Tech", "Development",\
    "Suppress Rebels", "Strengthen Government", "Artillery Barrage",\
    "Force March", "Generals", "Sonstiges", "Gesamt"]
    data, columns = mana_spent_table("mil", columns, header_labels, sg_id2)
    return render_template("show_stats/table.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            data = data, columns = columns, header_labels = header_labels, \
            colorize_columns = [i for i in range(1,len(header_labels))], \
            sort_by = len(header_labels) - 1, map = map, title = "MIL", mp = mp)

@show_stats.route("/reload_plot/<int:sg_id1>/<int:sg_id2>/<list:image_files>", methods = ["GET", "POST"])
def reload_plot(sg_id1, sg_id2, image_files):
    for file in image_files:
        plot = SavegamePlots.query.get(file)
        db.session.delete(plot)
        try:
            os.remove(os.path.join(current_app.root_path, "static/plots", file))
        except FileNotFoundError:
            pass
    db.session.commit()
    return redirect(redirect_url())

@show_stats.route("/reload_all_plots/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
def reload_all_plots(sg_id1, sg_id2):
    plots = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2)
    for plot in plots:
        filename = plot.filename
        db.session.delete(plot)
        try:
            os.remove(os.path.join(current_app.root_path, "static/plots", filename))
        except FileNotFoundError:
            pass
    db.session.commit()
    return redirect(redirect_url())

@show_stats.route("/victory_points/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def victory_points(sg_id1, sg_id2):
    mp = Savegame.query.get(sg_id2).mp
    institution = Savegame.query.get(sg_id2).institution

    if mp.id == 3:
        data, columns, header_labels = mp3_data(institution, mp, sg_id1, sg_id2)

    elif mp.id == 2:
        data, columns, header_labels = mp2_data(institution, mp, sg_id1, sg_id2)

    elif mp.id == 1:
        data, columns, header_labels = mp1_data(institution, mp, sg_id1, sg_id2)

    return render_template("show_stats/table.html", old_savegame = Savegame.query.get(sg_id1), \
            new_savegame = Savegame.query.get(sg_id2), \
            data = data, \
            columns = columns, header_labels = header_labels, \
            colorize_columns = [i for i in range(1,len(header_labels))], \
            sort_by = len(header_labels) - 1, mp = mp)
