import matplotlib.pyplot as plt
from statstool_web.models import *
import secrets
from sqlalchemy import desc

def get_colors_hex_hsl(sg_id, tag_list, model):
    nation_colors_hex = [model.query.filter_by(nation_tag = tag, \
            savegame_id = sg_id).first().color for tag in tag_list]
    nation_colors_hsl = [color.hsl for color in nation_colors_hex]

    return nation_colors_hex, nation_colors_hsl


def category_plot(sg_id1, sg_id2, category, tag_list, data_list, model, title):
    plot = SavegamePlots.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, type = category).first()
    if plot:
        return plot.filename
    else:
        figure = plt.figure(title)
        figure.suptitle(title, fontsize = 20)

        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.grid(True, axis="y")
        plt.minorticks_on()
        plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        plt.xticks(rotation = 15)

        delta_list = []
        for data in data_list:
            data = data.__dict__
            if sg_id1 != sg_id2:
                if NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, new_nation_tag = data["nation_tag"]).first():
                    plt.bar(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = data["nation_tag"]).first().nation_name, data[category], color = str(data["color"]), edgecolor = "grey", linewidth = 1)
                    old_tag = NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, new_nation_tag = data["nation_tag"]).first().old_nation_tag
                    try:
                        delta_list.append([NationSavegameData.query.filter_by(\
                            savegame_id = sg_id2, nation_tag = data["nation_tag"]).first().nation_name,data[category] - \
                            model.query.filter_by(nation_tag = old_tag, savegame_id = sg_id1).first().__dict__[category]])
                    except:
                        print(model,sg_id1,old_tag)
            else:
                plt.bar(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = data["nation_tag"]).first().nation_name, data[category], color = str(data["color"]), edgecolor = "grey", linewidth = 1)
                try:
                    delta_list.append([NationSavegameData.query.filter_by(\
                        savegame_id = sg_id2, nation_tag = data["nation_tag"]).first().nation_name,data[category] - \
                        model.query.filter_by(nation_tag = data["nation_tag"], savegame_id = sg_id1).first().__dict__[category]])
                except:
                    print(model,sg_id1,data["nation_tag"])

        delta_values = [x[1] for x in delta_list]
        norm = plt.Normalize(min(delta_values), max(delta_values))
        color_list = plt.cm.RdYlGn(norm(delta_values))

        for i in range(len(delta_list)):
            plt.bar(delta_list[i][0], delta_list[i][1], color = color_list[i], edgecolor = "grey", linewidth = 1)

        random = secrets.token_hex(8) + ".png"
        path = os.path.join(current_app.root_path, "static/plots", random)
        plt.savefig(path, dpi=200)
        filename = random
        plot = SavegamePlots(filename = filename, type = category, old_savegame_id = sg_id1, new_savegame_id = sg_id2)
        db.session.add(plot)
        db.session.commit()
        return filename


def get_images_and_table_data(categories, columns, model, sg_id1, sg_id2):
    old_year = Savegame.query.get(sg_id1).year
    new_year = Savegame.query.get(sg_id2).year
    tag_list = [nation.tag for nation in Savegame.query.get(sg_id2).player_nations]

    image_files = []
    data = []
    header_labels = ["Nation",old_year,new_year,"Δ","%"]
    table_columns = [0,1,2,3]
    for category, column in zip(categories,columns):
        data_list = model.query.filter(model.nation_tag.in_(tag_list),\
                model.savegame_id == sg_id1).order_by(desc(column))
        image_file1 = category_plot(sg_id1, sg_id1, category, tag_list, data_list, model, "{0}: {1}".format(category.replace("_"," ").title(),old_year))

        data_list = model.query.filter(model.nation_tag.in_(tag_list),\
                model.savegame_id == sg_id2).order_by(desc(column))
        image_file2 = category_plot(sg_id1, sg_id2, category, tag_list, data_list, model, "{0}: {1}-{2}".format(category.replace("_"," ").title(),old_year, new_year))

        image_files.append([image_file1, image_file2])

        d = table_data(category, old_year, new_year, tag_list, sg_id1, sg_id2, int, model)
        data.append(d)

    flattened_image_files = [file for sublist in image_files for file in sublist]
    map = Savegame.query.get(sg_id2).map_file
    ids = [i for i in range(len(image_files))]
    return zip(image_files, data, ids), ids, header_labels, table_columns, flattened_image_files, map


def table_data(category, old_year, new_year, tag_list, sg_id1, sg_id2, data_type, model):
    nation_data = []
    nation_names = []
    for new_tag in tag_list:
        data = []
        if NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, new_nation_tag = new_tag).first():
            old_tag = NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, new_nation_tag = new_tag).first().old_nation_tag
            for id,tag in zip((sg_id1,sg_id2),(old_tag,new_tag)):
                value = model.query.filter_by(nation_tag = tag, savegame_id = id).first().__dict__[category]
                data.append(value)
            delta = data_type(round(data[1] - data[0],2))
            if data[0] != 0:
                percent = round((data[1]/data[0]-1)*100,2)
                if delta > 0:
                    delta = "+" + str(delta)
                if percent > 0:
                    percent = "+" + str(percent)
                percent = str(percent) + "%"
            else:
                percent = "---"
            data.append(delta)
            data.append(percent)
            nation_data.append(data)
            nation_names.append(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = new_tag).first().nation_name)
    nation_colors_hex, nation_colors_hsl = get_colors_hex_hsl(sg_id2, tag_list, model)
    return zip(nation_data,nation_names,nation_colors_hex, nation_colors_hsl)


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
        nation_names = [NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).first().nation_name for nation in Savegame.query.get(sg_id2).player_nations]

        m = 0
        for tag, name in zip(nation_tags, nation_names):
            income_data = [(income.year,income.amount) for income in \
                    NationSavegameIncomePerYear.query.filter_by(nation_tag = tag, savegame_id = sg_id2).all() if income.year >= old_year]
            color = NationSavegameData.query.get((tag, sg_id2)).color
            marker = markers[a%len(markers)]
            plt.plot([x[0] for x in income_data], [x[1] for x in income_data], label = name, color = str(color), linewidth = 1.5, marker = marker, markersize = 3)
            if (n := max([y for (x,y) in income_data])) > m:
                m = n
            a += 1

        plt.axis([old_year, new_year, 0, m * 1.05])
        plt.legend(prop={'size': 8})

        random = secrets.token_hex(8) + ".png"
        path = os.path.join(current_app.root_path, "static/plots", random)
        plt.savefig(path, dpi=200)
        filename = random
        plot = SavegamePlots(filename = filename, type = category, old_savegame_id = sg_id1, new_savegame_id = sg_id2)
        db.session.add(plot)
        db.session.commit()


def mana_spent_table_total(header_labels, sg_id2):
    mana_data = []
    nation_names = []
    tag_list = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        tag_list.append(nation.tag)
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
        nation_names.append(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).first().nation_name)
    map = Savegame.query.get(sg_id2).map_file
    nation_colors_hex, nation_colors_hsl = get_colors_hex_hsl(sg_id2, tag_list, NationSavegameData)
    return zip(mana_data,nation_names,nation_colors_hex, nation_colors_hsl)


def mana_spent_table(category, columns, header_labels, sg_id2):
    mana_data = []
    nation_names = []
    tag_list = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        tag_list.append(nation.tag)
        data = {}
        for id in columns:
            data[id] = 0
        mana = NationSavegamePointsSpent.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag, points_spent_category = category).all()
        summe = 0
        for entry in mana:
            if entry.points_spent_id in columns:
                data[entry.points_spent_id] = entry.amount
                summe += entry.amount
        if mana:
            data["total"] = sum([x.amount for x in mana])
            data["rest"] = data["total"] - summe
        else:
            data["total"] = 0
            data["rest"] = 0

        mana_data.append(data)
        nation_names.append(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).first().nation_name)

    columns += ["rest", "total"]

    nation_colors_hex, nation_colors_hsl = get_colors_hex_hsl(sg_id2, tag_list, NationSavegameData)
    map = Savegame.query.get(sg_id2).map_file
    return zip(mana_data,nation_names,nation_colors_hex, nation_colors_hsl), columns
