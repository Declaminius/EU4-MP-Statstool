from flask import render_template, url_for, send_from_directory, request, redirect, flash
from statstool_web.forms import SavegameSelectForm, TagSetupForm, NewNationForm, NationFormationForm
from statstool_web import app, db
from statstool_web.parserfunctions import edit_parse, parse
from statstool_web.models import *
from werkzeug.utils import secure_filename
import os
import secrets
from pathlib import Path
from sqlalchemy.orm import load_only
from sqlalchemy import asc, desc
import matplotlib.pyplot as plt
from sqlalchemy.exc import IntegrityError

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
        old_tag_list = [nation.tag for nation in Savegame.query.get(sg_id1).player_nations]
        new_tag_list = [nation.tag for nation in Savegame.query.get(sg_id2).player_nations]
        for tag in old_tag_list:
            if tag in new_tag_list:
                formation = NationFormation(old_savegame_id = sg_id1, new_savegame_id = sg_id2, old_nation_tag = tag, new_nation_tag = tag)
                db.session.add(formation)
        try:
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
        else:
            db.session.commit()
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
    old_matching_tags = [x.old_nation_tag for x in NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2).all()]
    new_matching_tags = [x.new_nation_tag for x in NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2).all()]
    old_tag_list = [nation.tag for nation in Savegame.query.get(sg_id1).player_nations if nation.tag not in old_matching_tags]
    new_tag_list = [nation.tag for nation in Savegame.query.get(sg_id2).player_nations if nation.tag not in new_matching_tags]
    for field,tag_list in ((form.old_nation,old_tag_list), (form.new_nation,new_tag_list)):
        field.choices = \
            sorted([(tag,app.config["LOCALISATION_DICT"][tag]) \
            if tag in app.config["LOCALISATION_DICT"].keys() else (tag,tag) \
            for tag in tag_list], key = lambda x: x[1])
    for id in (sg_id1,sg_id2):
        savegame = Savegame.query.get(id)
        if not savegame.parse_flag:
            parse(savegame)

    nation_formations = [(x.old_nation_tag,x.new_nation_tag) for x in NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2).all()]
    return render_template("main.html", sg_id1 = sg_id1, sg_id2 = sg_id2, form = form, nation_formations = nation_formations)

@app.route("/main/<int:sg_id1>/<int:sg_id2>/remove_nation_formation/<string:old>/<string:new>", methods = ["GET", "POST"])
def remove_nation_formation(sg_id1,sg_id2,old,new):
    formation = NationFormation.query.get((sg_id1,sg_id2,old,new))
    db.session.delete(formation)
    db.session.commit()
    return redirect(url_for("main", sg_id1 = sg_id1, sg_id2 = sg_id2))

@app.route("/main/<int:sg_id1>/<int:sg_id2>/overview_table", methods = ["GET", "POST"])
def overview_table(sg_id1,sg_id2):
    random = secrets.token_hex(8) + ".json"
    path = os.path.join(app.root_path, 'json', random)
    columns = ["nation_tag", "great_power_score", "development", "effective_development", "navy_strength", "max_manpower", "income"]
    nation_data = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        data = NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).with_entities(*columns).first()._asdict()
        nation_data.append(data)
    return render_template("overview_table.html", sg_id1 = sg_id1, sg_id2 = sg_id2, data = nation_data, columns = columns)

@app.route("/main/<int:sg_id1>/<int:sg_id2>/test", methods = ["GET", "POST"])
def test(sg_id1, sg_id2):
    random = secrets.token_hex(8) + ".json"
    path = os.path.join(app.root_path, 'json', random)
    columns = ["nation_tag", "great_power_score", "development", "effective_development", "navy_strength", "max_manpower", "income"]
    nation_data = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        data = NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                savegame_id = sg_id2).with_entities(*columns).first()._asdict()
        nation_data.append(data)
    return render_template("test.html", sg_id1 = sg_id1, sg_id2 = sg_id2, data = nation_data, columns = columns)

@app.route("/main/<int:sg_id1>/<int:sg_id2>/development", methods = ["GET", "POST"])
def development(sg_id1, sg_id2):
    old_year = Savegame.query.get(sg_id1).year
    new_year = Savegame.query.get(sg_id2).year
    tag_list = [nation.tag for nation in Savegame.query.get(sg_id2).player_nations]
    dev_list = NationSavegameData.query.filter(NationSavegameData.nation_tag.in_(tag_list),\
                NationSavegameData.savegame_id == sg_id2).order_by(desc(NationSavegameData.development))
    eff_dev_list = NationSavegameData.query.filter(NationSavegameData.nation_tag.in_(tag_list),\
                NationSavegameData.savegame_id == sg_id2).order_by(desc(NationSavegameData.effective_development))

    category_plot(sg_id1,sg_id2,"development", tag_list, dev_list, NationSavegameData, "Development: {0}-{1}".format(old_year, new_year))
    category_plot(sg_id1,sg_id2,"effective_development", tag_list, eff_dev_list, NationSavegameData, "Effective Development: {0}-{1}".format(old_year, new_year))

    image_file1 = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = "development").first().filename
    image_file2 = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = "effective_development").first().filename
    return render_template("plot.html", sg_id1 = sg_id1, sg_id2 = sg_id2, image_files = [image_file1, image_file2])

def category_plot(sg_id1, sg_id2, category, tag_list, data_list, model, title):
    plot = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = category).first()
    if plot:
        return
    else:
        figure = plt.figure(title)
        figure.suptitle(title, fontsize = 20)

        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.grid(True, axis="y")
        plt.minorticks_on()

        delta_dev_list = []
        for data in data_list:
            data = data.__dict__
            plt.bar(data["nation_tag"], data[category], color = str(data["color"]), edgecolor = "grey", linewidth = 1)
            if NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, new_nation_tag = data["nation_tag"]).first():
                old_tag = NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, new_nation_tag = data["nation_tag"]).first().old_nation_tag
                delta_dev_list.append([data["nation_tag"],data[category] - model.query.filter_by(nation_tag = old_tag, savegame_id = sg_id1).first().__dict__[category]])
            else:
                delta_dev_list.append([data["nation_tag"],0])

        delta_values = [x[1] for x in delta_dev_list]
        norm = plt.Normalize(min(delta_values), max(delta_values))
        color_list = plt.cm.RdYlGn(norm(delta_values))

        for i in range(len(delta_dev_list)):
            plt.bar(delta_dev_list[i][0], delta_dev_list[i][1], color = color_list[i], edgecolor = "grey", linewidth = 1)

        random = secrets.token_hex(8) + ".png"
        path = os.path.join(app.root_path, "static/plots", random)
        plt.savefig(path, dpi=200)
        filename = url_for('static', filename='plots/' + random)
        plot = SavegamePlots(filename = filename, type = category, old_savegame_id = sg_id1, new_savegame_id = sg_id2)
        db.session.add(plot)
        db.session.commit()

@app.route("/main/<int:sg_id1>/<int:sg_id2>/income", methods = ["GET", "POST"])
def income(sg_id1, sg_id2):
    old_year = Savegame.query.get(sg_id1).year
    new_year = Savegame.query.get(sg_id2).year
    tag_list = [nation.tag for nation in Savegame.query.get(sg_id2).player_nations]
    income_list = NationSavegameData.query.filter(NationSavegameData.nation_tag.in_(tag_list),\
                NationSavegameData.savegame_id == sg_id2).order_by(desc(NationSavegameData.income))
    category_plot(sg_id1,sg_id2,"income", tag_list, income_list, NationSavegameData, "Income: {0}-{1}".format(old_year, new_year))
    image_file1 = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = "income").first().filename
    return render_template("plot.html", sg_id1 = sg_id1, sg_id2 = sg_id2, image_files = [image_file1])

@app.route("/main/<int:sg_id1>/<int:sg_id2>/max_manpower", methods = ["GET", "POST"])
def max_manpower(sg_id1, sg_id2):
    old_year = Savegame.query.get(sg_id1).year
    new_year = Savegame.query.get(sg_id2).year
    tag_list = [nation.tag for nation in Savegame.query.get(sg_id2).player_nations]
    manpower_list = NationSavegameData.query.filter(NationSavegameData.nation_tag.in_(tag_list),\
                NationSavegameData.savegame_id == sg_id2).order_by(desc(NationSavegameData.max_manpower))
    category_plot(sg_id1,sg_id2,"max_manpower", tag_list, manpower_list, NationSavegameData, "Maximum Manpower: {0}-{1}".format(old_year, new_year))
    image_file1 = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = "max_manpower").first().filename
    return render_template("plot.html", sg_id1 = sg_id1, sg_id2 = sg_id2, image_files = [image_file1])

@app.route("/main/<int:sg_id1>/<int:sg_id2>/army_losses", methods = ["GET", "POST"])
def army_losses(sg_id1, sg_id2):
    old_year = Savegame.query.get(sg_id1).year
    new_year = Savegame.query.get(sg_id2).year
    tag_list = [nation.tag for nation in Savegame.query.get(sg_id2).player_nations]
    image_files = []
    columns = ( NationSavegameArmyLosses.infantry,NationSavegameArmyLosses.cavalry,NationSavegameArmyLosses.artillery,\
                NationSavegameArmyLosses.combat,NationSavegameArmyLosses.attrition,NationSavegameArmyLosses.total)
    for category, column in zip(("Infantry", "Cavalry", "Artillery", "Combat", "Attrition", "Total"),columns):
        army_losses_list = NationSavegameArmyLosses.query.filter(NationSavegameArmyLosses.nation_tag.in_(tag_list),\
                    NationSavegameArmyLosses.savegame_id == sg_id2).order_by(desc(column))
        category_plot(sg_id1, sg_id2, category.lower(), tag_list, army_losses_list, NationSavegameArmyLosses, "Army Losses - {0}: {1}-{2}".format(category, old_year, new_year))
        image_files.append(SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = category.lower()).first().filename)
    return render_template("plot.html", sg_id1 = sg_id1, sg_id2 = sg_id2, image_files = image_files)

@app.route("/main/<int:sg_id1>/<int:sg_id2>/income_over_time", methods = ["GET", "POST"])
def income_over_time(sg_id1, sg_id2):
    old_year = Savegame.query.get(sg_id1).year
    new_year = Savegame.query.get(sg_id2).year
    income_plot("income_over_time_total", 1445, new_year, sg_id1, sg_id2)
    income_plot("income_over_time_latest", old_year, new_year, sg_id1, sg_id2)
    image_file1 = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = "income_over_time_total").first().filename
    image_file2 = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = "income_over_time_latest").first().filename
    return render_template("plot.html", sg_id1 = sg_id1, sg_id2 = sg_id2, image_files = [image_file1, image_file2])

def income_plot(category, old_year, new_year, sg_id1, sg_id2):
    plot = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = category).first()
    if plot:
        return
    else:
        income_plot = plt.figure("Income-Plot:{0}-{1}".format(old_year,new_year))
        income_plot.suptitle("{0}-{1}".format(old_year,new_year), fontsize = 20)
        plt.grid(True, which="both")
        plt.minorticks_on()
        plt.xlabel("Year")
        plt.ylabel("Income Per Year")
        a = 0
        markers = ["o","v","^","<",">","s","p","*","+","x","d","D","h","H"]
        nation_tags = [nation.tag for nation in Savegame.query.get(sg_id2).player_nations]

        m = 0
        for tag in nation_tags:
            income_data = [(income.year,income.amount) for income in \
                    NationSavegameIncomePerYear.query.filter_by(nation_tag = tag, savegame_id = sg_id2).all() if income.year >= old_year]
            color = NationSavegameData.query.get((tag, sg_id2)).color
            marker = markers[a%len(markers)]
            plt.plot([x[0] for x in income_data], [x[1] for x in income_data], label=tag, color= str(color), linewidth=1.5, marker = marker, markersize = 3)
            if (n := max([y for (x,y) in income_data])) > m:
                m = n
            a += 1

        plt.axis([old_year, new_year, 0, m * 1.05])
        plt.legend(prop={'size': 8})

        random = secrets.token_hex(8) + ".png"
        path = os.path.join(app.root_path, "static/plots", random)
        plt.savefig(path, dpi=200)
        filename = url_for('static', filename='plots/' + random)
        plot = SavegamePlots(filename = filename, type = category, old_savegame_id = sg_id1, new_savegame_id = sg_id2)
        db.session.add(plot)
        db.session.commit()

@app.route("/main/<int:sg_id1>/<int:sg_id2>/<image_files>/reload_plot", methods = ["GET", "POST"])
def reload_plot(sg_id1, sg_id2, image_files):
    old_year = Savegame.query.get(sg_id1).year
    new_year = Savegame.query.get(sg_id2).year
    income_plot("income_over_time_total", 1445, new_year, sg_id1, sg_id2)
    income_plot("income_over_time_latest", old_year, new_year, sg_id1, sg_id2)
    image_file1 = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = "income_over_time_total").first().filename
    image_file2 = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = "income_over_time_latest").first().filename
    return render_template("plot.html", sg_id1 = sg_id1, sg_id2 = sg_id2, image_files = [image_file1, image_file2])
