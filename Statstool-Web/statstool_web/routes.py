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
    form = NationFormationForm()
    for field,id in ((form.old_nation,sg_id1), (form.new_nation,sg_id2)):
        tag_list = [nation.tag for nation in Savegame.query.get(id).player_nations]
        field.choices = \
            sorted([(tag,app.config["LOCALISATION_DICT"][tag]) \
            if tag in app.config["LOCALISATION_DICT"].keys() else (tag,tag) \
            for tag in tag_list], key = lambda x: x[1])
    for id in (sg_id1,sg_id2):
        savegame = Savegame.query.get(id)
        if not savegame.parse_flag:
            parse(savegame)
    return render_template("main.html", sg_id1 = sg_id1, sg_id2 = sg_id2, form = form)

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
    savegame2 = Savegame.query.get(sg_id2)
    development_figure = plt.figure("Development - {0}".format(savegame2.year))

    ax1 = plt.subplot2grid((2, 1), (0, 0))
    ax2 = plt.subplot2grid((2, 1), (1, 0), sharey=ax1)

    ax1.tick_params(axis='both', which='major', labelsize=8)
    ax2.tick_params(axis='both', which='major', labelsize=8)

    plt.subplots_adjust(hspace = 0.3)
    development_figure.suptitle(savegame2.year, fontsize = 20)
    #development_figure.set_size_inches(16, 8)

    ax1.grid(True, axis="y")
    ax1.minorticks_on()
    ax1.set_title("Development")

    ax2.grid(True, axis="y")
    ax2.minorticks_on()
    ax2.set_title("Effective Development")

    tag_list = [nation.tag for nation in savegame2.player_nations]
    data_list = NationSavegameData.query.filter(NationSavegameData.nation_tag.in_(tag_list),\
                NationSavegameData.savegame_id == sg_id2).order_by(desc(NationSavegameData.development))

    #color_list, delta_dev = delta("development", "delta_dev")

    for data in data_list:
        ax1.bar(data.nation_tag, data.development, color = str(data.color), edgecolor = "grey", linewidth = 1)

    data_list = NationSavegameData.query.filter(NationSavegameData.nation_tag.in_(tag_list), \
                NationSavegameData.savegame_id == sg_id2).order_by(desc(NationSavegameData.effective_development))
    for data in data_list:
        ax2.bar(data.nation_tag, data.effective_development, color = str(data.color), edgecolor = "grey", linewidth = 1)

    # if compare:
    #     ax1.bar(range(len(delta_dev)), delta_dev, label = "Spieltag-Ende", color = color_list, edgecolor = "black", linewidth = 1)
    #
    #     color_list, delta_eff_dev_plot = self.delta("effective_development", "delta_eff_dev")
    #     delta_eff_dev_table = [x for _,x in sorted(zip([savegame.stats_dict[tag]["development"]\
    #     for tag in savegame.stats_dict.keys()],[savegame.stats_dict[tag]["delta_eff_dev"]\
    #     for tag in savegame.stats_dict.keys()]), reverse = True)]
    #    ax2.bar(range(len(delta_eff_dev_plot)), delta_eff_dev_plot, label = "Spieltag-Ende", color = color_list, edgecolor = "black", linewidth = 1)

    # colors = []
    # cell_text = []
    # cell_text.append(["" for x in dev])
    # cell_text.append([int(value) for value,tag in dev])
    # cell_text.append([int(x[0]) for x in eff_dev_table])
    # if compare:
    #     cell_text.append(["" for x in dev])
    #     cell_text.append(["+{}".format(int(a)) if a > 0 else str(int(a)) for a in delta_dev])
    #     cell_text.append(["+{}".format(int(a)) if a > 0 else str(int(a)) for a in delta_eff_dev_table])
    #     cell_text.append(["" for x in dev])
    #     cell_text.append([int(a[0] - b) for a,b in zip(dev, delta_dev)])
    #     cell_text.append([int(a[0] - b) for a,b in zip(eff_dev_table, delta_eff_dev_table)])
    #     rows = [savegame.year, "Development", "Effective Development", self.savegame_list[2].year, "Development", "Effective Development", self.savegame_list[0].year, "Development", "Effective Development"]
    #     row_colors = ["white", "gold", "salmon", "white", "gold", "salmon", "white", "gold", "salmon"]
    # else:
    #     rows = [savegame.year, "Development", "Effective Development"]
    #     row_colors = ["white", "gold", "salmon"]
    # for data in cell_text:
    #     try:
    #         clean_data = [float(d) for d in data]
    #         norm = plt.Normalize(min(clean_data), max(clean_data))
    #         colors.append(plt.cm.RdYlGn(norm(clean_data)))
    #     except:
    #         colors.append(["white" for x in dev])
    # col_colors = []
    # for value,tag in dev:
    #     if tag in savegame.color_dict:
    #         col_colors.append(savegame.color_dict[tag])
    #     else:
    #         col_colors.append("black")
    # cols = [x[1] for x in dev]
    #
    #
    # tab = ax3.table(cellText=cell_text, cellColours=colors, rowLabels=rows, rowColours=row_colors,
    #                 colColours=col_colors, colLabels=cols, loc='center')
    # tab.auto_set_font_size(False)
    # tab.set_fontsize(10)
    # table_props = tab.properties()
    # table_cells = table_props['children']
    # for cell in table_cells:
    #     cell.set_height(0.2)
    # ax3.axis("Off")
    random = secrets.token_hex(8) + ".png"
    path = os.path.join(app.root_path, "static/plots", random)
    plt.savefig(path, dpi=200)
    image_file = url_for('static', filename='plots/' + random)
    return render_template("plot.html", sg_id1 = sg_id1, sg_id2 = sg_id2, image_files = [image_file])


def delta(self, category_str, delta_str):
    for tag in self.savegame_list[1].stats_dict.keys():
        if (tag in self.formable_nations_dict.keys()) and \
        (self.formable_nations_dict[tag] in self.savegame_list[0].stats_dict.keys()):
            self.savegame_list[1].stats_dict[tag][delta_str] = self.savegame_list[1].stats_dict[tag][category_str]\
                - self.savegame_list[0].stats_dict[self.formable_nations_dict[tag]][category_str]
        else:
            self.savegame_list[1].stats_dict[tag][delta_str] =  self.savegame_list[1].stats_dict[tag][category_str]\
            - self.savegame_list[0].stats_dict[tag][category_str]
    values = [x for _,x in sorted(zip([self.savegame_list[1].stats_dict[tag][category_str]\
    for tag in self.savegame_list[1].stats_dict.keys()],[self.savegame_list[1].stats_dict[tag][delta_str]\
    for tag in self.savegame_list[1].stats_dict.keys()]), reverse = True)]
    norm = plt.Normalize(min(values), max(values))
    color_list = plt.cm.RdYlGn(norm(values))
    return color_list, values

@app.route("/main/<int:sg_id1>/<int:sg_id2>/income_over_time", methods = ["GET", "POST"])
def income_over_time(sg_id1, sg_id2):
    old_year = Savegame.query.get(sg_id1).year
    new_year = Savegame.query.get(sg_id2).year
    image_file1 = income_plot(1445, new_year, sg_id2)
    image_file2 = income_plot(old_year, new_year, sg_id2)
    return render_template("plot.html", sg_id1 = sg_id1, sg_id2 = sg_id2, image_files = [image_file1, image_file2])

def income_plot(old_year, new_year, sg_id2):
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
    return url_for('static', filename='plots/' + random)
