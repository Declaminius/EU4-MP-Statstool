from flask import render_template, url_for, request, redirect, flash, abort, Blueprint, current_app
from statstool_web.show_stats.forms import NationFormationForm
from statstool_web.show_stats.util import category_plot, table_data, get_images_and_table_data, income_plot
from statstool_web import db, bcrypt
from statstool_web.models import *
from statstool_web.util import redirect_url
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_required
import statstool_web.parserfunctions

import os
import secrets
import matplotlib
import matplotlib.pyplot as plt

show_stats = Blueprint('show_stats', __name__)

matplotlib.use('Agg')

@show_stats.route("/parse/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def parse(sg_id1,sg_id2):
    for id in (sg_id1,sg_id2):
        savegame = Savegame.query.get(id)
        if not savegame.parse_flag:
            statstool_web.parserfunctions.parse(savegame)
            if savegame.parse_flag:
                try:
                    os.remove(os.path.join(current_app.root_path, current_app.config["UPLOAD_FOLDER"], savegame.file))
                except FileNotFoundError:
                    pass

    old_savegame = Savegame.query.get(sg_id1)
    new_savegame = Savegame.query.get(sg_id2)
    for nation in new_savegame.player_nations:
        if nation not in old_savegame.player_nations:
            if nation in old_savegame.nations:
                old_savegame.player_nations.append(nation)
            else:
                continue
        if NationFormation.query.get((sg_id1,sg_id2,nation.tag,nation.tag)) is None:
            formation = NationFormation(old_savegame_id = sg_id1, new_savegame_id = sg_id2, old_nation_tag = nation.tag, new_nation_tag = nation.tag)
            db.session.add(formation)
    db.session.commit()
    if current_user.is_authenticated and sg_id1 != sg_id2:
        return redirect(url_for("show_stats.configure", sg_id1 = sg_id1, sg_id2 = sg_id2))
    else:
        return redirect(url_for("show_stats.overview_table", sg_id1 = sg_id1, sg_id2 = sg_id2))

@show_stats.route("/map/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def map(sg_id1,sg_id2):
    return render_template("show_stats_layout.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2))

@show_stats.route("/remove_nation_formation/<int:sg_id1>/<int:sg_id2>/<string:old>/<string:new>", methods = ["GET", "POST"])
def remove_nation_formation(sg_id1,sg_id2,old,new):
    formation = NationFormation.query.get((sg_id1,sg_id2,old,new))
    db.session.delete(formation)
    db.session.commit()
    return redirect(url_for("show_stats.parse", sg_id1 = sg_id1, sg_id2 = sg_id2))

@show_stats.route("/configure/<int:sg_id1>/<int:sg_id2>", methods = ["GET", "POST"])
@login_required
def configure(sg_id1,sg_id2):
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
        old_nation = NationSavegameData.query.filter_by(savegame_id = sg_id1, nation_tag = x.old_nation_tag).first().nation_name
        new_nation = NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = x.new_nation_tag).first().nation_name
        nation_formations.append((old_nation, new_nation))
    return render_template("configure.html", old_savegame = old_savegame, new_savegame = new_savegame, form = form, nation_formations = nation_formations)

@show_stats.route("/overview_table/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def overview_table(sg_id1,sg_id2):
    columns = ["great_power_score", "development", "effective_development", "navy_strength", "max_manpower", "income"]
    header_labels = ["Nation", "Great Power Score", "Development", "Effective Development", "Navy Strength", "Maximum Manpower", "Monthly Income"]
    nation_data = []
    nation_colors_hex = []
    nation_colors_hsl = []
    nation_names = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        data = NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).with_entities(*columns).first()._asdict()
        nation_data.append(data)
        nation_colors_hex.append( NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first().color)
        nation_colors_hsl.append( NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first().color.hsl)
        nation_names.append(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).first().nation_name)
    return render_template("table.html", old_savegame = Savegame.query.get(sg_id1), \
            new_savegame = Savegame.query.get(sg_id2), data = zip(nation_data,nation_names,nation_colors_hex, nation_colors_hsl), \
            columns = columns, header_labels = header_labels, colorize_columns = [1,2,3,4,5,6], sort_by = 1, map = map)

@show_stats.route("/development/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def development(sg_id1, sg_id2):

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(("development","effective_development"), \
            (NationSavegameData.development,NationSavegameData.effective_development), NationSavegameData, sg_id1, sg_id2)
    return render_template("plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            flattened_image_files = flattened_image_files, content = content, ids = ids, header_labels = header_labels, columns = columns, map = map)

@show_stats.route("/income/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def income(sg_id1, sg_id2):

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(["income"], [NationSavegameData.income], NationSavegameData, sg_id1, sg_id2)

    return render_template("plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            content = content, ids = ids, header_labels = header_labels, columns = columns, map = map)

@show_stats.route("/max_manpower/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def max_manpower(sg_id1, sg_id2):

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(["max_manpower"], [NationSavegameData.max_manpower], NationSavegameData, sg_id1, sg_id2)

    return render_template("plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            content = content, ids = ids, header_labels = header_labels, columns = columns, map = map)

@show_stats.route("/army_losses/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def army_losses(sg_id1, sg_id2):
    categories = ("infantry", "cavalry", "artillery", "combat", "attrition", "total")
    columns = ( NationSavegameArmyLosses.infantry,NationSavegameArmyLosses.cavalry,NationSavegameArmyLosses.artillery,\
                NationSavegameArmyLosses.combat,NationSavegameArmyLosses.attrition,NationSavegameArmyLosses.total)

    content, ids, header_labels, columns, flattened_image_files, map = get_images_and_table_data(categories, columns, NationSavegameArmyLosses, sg_id1, sg_id2)

    return render_template("plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
            content = content, ids = ids, header_labels = header_labels, columns = columns, map = map)

@show_stats.route("/income_over_time/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def income_over_time(sg_id1, sg_id2):

    new_year = Savegame.query.get(sg_id2).year
    image_files = []
    for (old_year, category) in zip((1445,Savegame.query.get(sg_id1).year),("income_over_time_total","income_over_time_latest")):
        income_plot(category, old_year, new_year, sg_id1, sg_id2)
        image_files.append(SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = category).first().filename)
    map = Savegame.query.get(sg_id2).map_file
    return render_template("income_plot.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), image_files = image_files, map = map)

@show_stats.route("/provinces/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def provinces(sg_id1, sg_id2):
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
            nation_colors.append(str(owner.color))
        else:
            nation_colors.append("#ffffff")
        nation_tags.append(province["nation_tag"])
        trade_good_name = TradeGood.query.filter_by(id = province["trade_good_id"]).first().name
        data["trade_good_name"] = trade_good_name
        province = Province.query.filter_by(id = province["province_id"]).first()
        data["name"] = province.name
        province_data.append(data)

    columns.append("trade_good_name")
    columns.insert(1, "name")
    return render_template("province_table.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
        data = zip(province_data,nation_tags,nation_colors), columns = columns, header_labels = header_labels)

@show_stats.route("/army_battles/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def army_battles(sg_id1, sg_id2):
    columns = ["date", "attacker_country", "attacker_infantry", "attacker_cavalry", \
        "attacker_artillery", "attacker_total", "attacker_losses", "attacker_commander", \
        "defender_country", "defender_infantry", "defender_cavalry", \
        "defender_artillery", "defender_total", "defender_losses", "defender_commander", "total_combatants", "total_losses"]
    header_labels = ["Datum", "Angreifer", "Inf", "Kav", "Art", "Gesamt", "Verluste", "General", \
        "Verteidiger", "Inf", "Kav", "Art", "Gesamt", "Verluste", "General", "Truppen", "Verluste"]
    battle_data = []
    nation_colors = []
    nation_tags = []
    for battle in ArmyBattle.query.filter_by(savegame_id = sg_id2).all():
        battle = battle.__dict__
        data = {x: [battle[x],"#ffffff"] for x in columns}
        for column in ("attacker_country","defender_country"):
            nation = NationSavegameData.query.filter_by(nation_tag = data[column][0], savegame_id = sg_id2).first()
            if nation:
                data[column][1] = str(nation.color)
        result = battle["result"]
        if result == "yes":
            data["attacker_commander"][1] = "00ff00"
            data["defender_commander"][1] = "ff0000"
        if result == "no":
            data["attacker_commander"][1] = "ff0000"
            data["defender_commander"][1] = "00ff00"
        battle_data.append(data)

    return render_template("army_battles_table.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
        data = battle_data, columns = columns, header_labels = header_labels)

@show_stats.route("/mana_spent/<int:sg_id1>/<int:sg_id2>", methods = ["GET"])
def mana_spent(sg_id1, sg_id2):
    columns = ["adm", "dip", "mil", "total"]
    header_labels = ["Nation", "ADM", "DIP", "MIL", "Total"]
    mana_data = []
    nation_colors_hex = []
    nation_colors_hsl = []
    nation_names = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        data = {}
        mana = NationSavegamePointsSpent.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).all()
        if mana:
            data["total"] = sum([x.amount for x in mana])
            for category in ("adm", "dip", "mil"):
                mana = NationSavegamePointsSpent.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag, points_spent_category = category).all()
                if mana:
                    data[category] = sum([x.amount for x in mana])
                else:
                    data[category] = 0
        else:
            for category in ("adm", "dip", "mil", "total"):
                data[category] = 0
        mana_data.append(data)
        nation_colors_hex.append(NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first().color)
        nation_colors_hsl.append(NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first().color.hsl)
        nation_names.append(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).first().nation_name)
    map = Savegame.query.get(sg_id2).map_file
    return render_template("table.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
        data = zip(mana_data,nation_names,nation_colors_hex, nation_colors_hsl), columns = columns, header_labels = header_labels, colorize_columns = [1,2,3,4], sort_by = 4, map = map)

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
    columns = ["standing_army", "navy_cannons"]
    header_labels = ["Nation", "Stehendes Heer", "Flotte: Gesamtanzahl Kanonen", "Armeeverluste im Kampf", "höchstentwickelte Provinz", "Siegpunkte"]
    min_values = {"standing_army": 100000, "navy_cannons": 2000, "losses": 500000, "highest_dev": 50}

    if mp.id == 0:

        if institution is Institutions.renaissance:
            header_labels.insert(1,"Höchste AE")
            columns.insert(0, "highest_ae")
            min_values["highest_ae"] = 50

        if institution is Institutions.colonialism:
            header_labels.insert(1, "Meiste laufende Kolonien")
            columns.insert(0, "num_of_colonies")
            min_values["num_of_colonies"] = 5

        if institution is Institutions.printing_press:
            header_labels.insert(1, "Meiste konvertierte Provinzen")
            columns.insert(0, "num_converted_religion")
            min_values["num_converted_religion"] = 0

        if institution is Institutions.global_trade:
            header_labels.insert(1, "Globaler Handel")

        if institution is Institutions.manufactories:
            header_labels.insert(1, "Meister Produktionsführer")
            columns.insert(0, "num_of_production_leaders")
            min_values["num_of_production_leaders"] = 3

        if institution is Institutions.enlightenment:
             header_labels.insert(1, "Innovativität")
             columns.insert(0, "innovativeness")
             min_values["innovativeness"] = 50

        if institution is Institutions.industrialization:
            header_labels.insert(1, "InGame-Score")
            columns.insert(0, "score")
            min_values["score"] = 0

    nation_data = []
    nation_colors_hex = []
    nation_colors_hsl = []
    nation_names = []
    nation_tags = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        data = NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).with_entities(*columns).first()._asdict()
        nation_colors_hex.append(NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first().color)
        nation_colors_hsl.append(NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first().color.hsl)
        nation_names.append(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).first().nation_name)
        nation_tags.append(nation.tag)

        losses = NationSavegameArmyLosses.query.filter_by(nation_tag = nation.tag, savegame_id = sg_id2).first().combat - NationSavegameArmyLosses.query.filter_by(nation_tag = nation.tag, savegame_id = sg_id1).first().combat
        data["losses"] = losses

        nation_savegame_data = NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).first()
        if nation_savegame_data.highest_dev_province_id:
            result = NationSavegameProvinces.query.get((sg_id2, nation_savegame_data.highest_dev_province_id))
            data["highest_dev"] = result.development
            data["highest_dev_province_id"] = nation_savegame_data.highest_dev_province_id
        else:
            forbidden_ids = [sg.highest_dev_province_id for sg in mp.savegames if sg.year < Savegame.query.get(sg_id2).year and sg.highest_dev_province_id]
            print(forbidden_ids)
            highest_dev_province = NationSavegameProvinces.query.filter(NationSavegameProvinces.province_id.notin_(forbidden_ids)).filter_by( \
                    nation_tag = nation.tag, savegame_id = sg_id2).order_by(NationSavegameProvinces.development.desc()).first()
            nation_savegame_data.highest_dev_province_id = highest_dev_province.province_id
            data["highest_dev"] = highest_dev_province.development
            data["highest_dev_province_id"] = highest_dev_province.province_id

        data["victory_points"] = 0
        nation_data.append(data)

    columns += ["losses", "highest_dev", "victory_points"]
    nation_names.append("Minimalwert")
    nation_colors_hex.append("ffffff")
    nation_colors_hsl.append([0,0,1])
    nation_data.append(min_values)

    for category in min_values.keys():
        max_category = max([x[category] for x in nation_data])
        for data in nation_data[:-1]:
            if data[category] == max_category:
                data["victory_points"] += 1
                if category == "highest_dev":
                    savegame = Savegame.query.get(sg_id2)
                    savegame.highest_dev_province_id = data["highest_dev_province_id"]

    for data, tag in zip(nation_data[:-1], nation_tags):
        if not VictoryPoints.query.filter_by(mp_id = Savegame.query.get(sg_id2).mp_id, institution = institution, nation_tag = tag).first():
            vp = VictoryPoints(mp_id = Savegame.query.get(sg_id2).mp_id, institution = institution, nation_tag = tag, victory_points = data["victory_points"])
            db.session.add(vp)
    db.session.commit()

    return render_template("table.html", old_savegame = Savegame.query.get(sg_id1), new_savegame = Savegame.query.get(sg_id2), \
        data = zip(nation_data,nation_names,nation_colors_hex,nation_colors_hsl), columns = columns, header_labels = header_labels, colorize_columns = [1,2,3,4,5], sort_by = 5)
