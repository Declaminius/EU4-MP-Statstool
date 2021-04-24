from statstool_web.models import *


def mp1_data(institution, mp, sg_id1, sg_id2):
    columns = ["standing_army", "navy_cannons"]
    header_labels = ["Nation", "Stehendes Heer", "Flotte: Gesamtanzahl Kanonen", "Armeeverluste im Kampf", "höchstentwickelte Provinz", "Siegpunkte"]
    min_values = {"standing_army": 100000, "navy_cannons": 2000, "losses": 500000, "highest_dev": 50}

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

    if institution is Institutions.industrialization:
        header_labels.insert(1, "InGame-Score")
        columns.insert(0, "score")
        min_values["score"] = 0

    if institution is Institutions.manufactories:
        header_labels.insert(1, "Meister Produktionsführer")
        columns.insert(0, "num_of_production_leaders")
        min_values["num_of_production_leaders"] = 3

    if institution is Institutions.enlightenment:
         header_labels.insert(1, "Innovativität")
         columns.insert(0, "innovativeness")
         min_values["innovativeness"] = 50

    nation_data = []
    nation_colors_hex = []
    nation_colors_hsl = []
    nation_names = []
    nation_tags = []
    for nation in Savegame.query.get(sg_id2).player_nations:
        old_nation = NationFormation.query.filter_by(old_savegame_id = sg_id1, new_savegame_id = sg_id2, new_nation_tag = nation.tag).first()
        if old_nation:
            old_tag = old_nation.old_nation_tag
            data = NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                    savegame_id = sg_id2).with_entities(*columns).first()._asdict()
            nation_colors_hex.append(NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                    savegame_id = sg_id2).first().color)
            nation_colors_hsl.append(NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                    savegame_id = sg_id2).first().color.hsl)
            nation_names.append(NationSavegameData.query.filter_by(savegame_id = sg_id2, nation_tag = nation.tag).first().nation_name)
            nation_tags.append(nation.tag)


            losses = NationSavegameArmyLosses.query.filter_by(nation_tag = nation.tag, savegame_id = sg_id2).first().combat - NationSavegameArmyLosses.query.filter_by(nation_tag = old_tag, savegame_id = sg_id1).first().combat
            data["losses"] = losses
            nation_savegame_data = NationSavegameData.query.filter_by(nation_tag = nation.tag, \
                    savegame_id = sg_id2).first()
            if nation_savegame_data.highest_dev_province_id:
                result = NationSavegameProvinces.query.get((sg_id2, nation_savegame_data.highest_dev_province_id))
                data["highest_dev"] = result.development
                data["highest_dev_province_id"] = nation_savegame_data.highest_dev_province_id
            else:
                forbidden_ids = [sg.highest_dev_province_id for sg in mp.savegames if sg.year < Savegame.query.get(sg_id2).year and sg.highest_dev_province_id]
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
                if category in ("highest_ae", "num_of_colonies", "num_converted_religion", "num_of_production_leaders", "innovativeness", "score"):
                    data["victory_points"] += 2
                else:
                    data["victory_points"] += 1
                if category == "highest_dev":
                    savegame = Savegame.query.get(sg_id2)
                    savegame.highest_dev_province_id = data["highest_dev_province_id"]

    for data, tag in zip(nation_data[:-1], nation_tags):
        if not VictoryPoints.query.filter_by(mp_id = Savegame.query.get(sg_id2).mp_id, institution = institution, nation_tag = tag).first():
            vp = VictoryPoints(mp_id = Savegame.query.get(sg_id2).mp_id, institution = institution, nation_tag = tag, victory_points = data["victory_points"])
            db.session.add(vp)
        else:
            vp = VictoryPoints.query.filter_by(mp_id = Savegame.query.get(sg_id2).mp_id, institution = institution, nation_tag = tag).first()
            vp.victory_points = data["victory_points"]
    db.session.commit()

    return zip(nation_data,nation_names,nation_colors_hex,nation_colors_hsl), columns, header_labels


def mp2_data(institution, mp, sg_id1, sg_id2):
    columns = ["standing_army", "navy_cannons"]
    header_labels = ["Nation", "Stehendes Heer", "Flotte: Gesamtanzahl Kanonen", "Armeeverluste im Kampf", "höchstentwickelte Provinz", "Siegpunkte"]
    min_values = {"standing_army": 100000, "navy_cannons": 2000, "losses": 500000, "highest_dev": 50}

    if institution is Institutions.manufactories:
        header_labels.insert(1, "Meister Produktionsführer")
        columns.insert(0, "num_of_production_leaders")
        min_values["num_of_production_leaders"] = 3

    if institution is Institutions.enlightenment:
         header_labels.insert(1, "Innovativität")
         columns.insert(0, "innovativeness")
         min_values["innovativeness"] = 50

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
                if category in ("highest_ae", "num_of_colonies", "num_converted_religion", "num_of_production_leaders", "innovativeness", "score"):
                    data["victory_points"] += 2
                else:
                    data["victory_points"] += 1
                if category == "highest_dev":
                    savegame = Savegame.query.get(sg_id2)
                    savegame.highest_dev_province_id = data["highest_dev_province_id"]

    for data, tag in zip(nation_data[:-1], nation_tags):
        if not VictoryPoints.query.filter_by(mp_id = Savegame.query.get(sg_id2).mp_id, institution = institution, nation_tag = tag).first():
            vp = VictoryPoints(mp_id = Savegame.query.get(sg_id2).mp_id, institution = institution, nation_tag = tag, victory_points = data["victory_points"])
            db.session.add(vp)
        else:
            vp = VictoryPoints.query.filter_by(mp_id = Savegame.query.get(sg_id2).mp_id, institution = institution, nation_tag = tag).first()
            vp.victory_points = data["victory_points"]
    db.session.commit()

    return zip(nation_data,nation_names,nation_colors_hex,nation_colors_hsl), columns, header_labels


def mp3_data(institution, mp, sg_id1, sg_id2):
    columns = []
    header_labels = ["Team", "Armeeverluste im Kampf", "höchstentwickelte Provinz", "Siegpunkte"]

    team_data = []
    team_colors_hex = []
    team_colors_hsl = []
    team_names = []
    team_ids = []
    for team in mp.teams:
        data = {}
        team_colors_hex.append("#ffffff")
        team_colors_hsl.append((0,0,100))
        team_names.append("Team {}".format(team.id))
        team_ids.append(team.id)
        team_tags = (team.team_tag1, team.team_tag2)

        losses = 0
        highest_dev = 0
        for tag in team_tags:
            losses += NationSavegameArmyLosses.query.filter_by(nation_tag = tag,\
                    savegame_id = sg_id2).first().combat - NationSavegameArmyLosses.query.filter_by(\
                    nation_tag = tag, savegame_id = sg_id1).first().combat

            nation_savegame_data = NationSavegameData.query.filter_by(nation_tag = tag, \
                savegame_id = sg_id2).first()
            if nation_savegame_data.highest_dev_province_id:
                highest_dev_province = NationSavegameProvinces.query.get((sg_id2, nation_savegame_data.highest_dev_province_id))
                if highest_dev_province.development > highest_dev:
                    highest_dev_province_id = nation_savegame_data.highest_dev_province_id
                    highest_dev = highest_dev_province.development
            else:
                forbidden_ids = [sg.highest_dev_province_id for sg in mp.savegames\
                                if sg.year < Savegame.query.get(sg_id2).year and sg.highest_dev_province_id]
                highest_dev_province = NationSavegameProvinces.query.filter(\
                        NationSavegameProvinces.province_id.notin_(forbidden_ids)).filter_by(\
                        nation_tag = tag, savegame_id = sg_id2).order_by(NationSavegameProvinces.development.desc()).first()

                nation_savegame_data.highest_dev_province_id = highest_dev_province.province_id
                if highest_dev_province.development > highest_dev:
                    highest_dev_province_id = nation_savegame_data.highest_dev_province_id
                    highest_dev = highest_dev_province.development

        data["losses"] = losses
        data["highest_dev"] = highest_dev
        data["highest_dev_province_id"] = highest_dev_province_id
        data["victory_points"] = 0
        team_data.append(data)

    columns += ["losses", "highest_dev"]

    for category in columns:
        max_category = max([x[category] for x in team_data])
        for data in team_data[:-1]:
            if data[category] == max_category:
                data["victory_points"] += 1
                if category == "highest_dev":
                    savegame = Savegame.query.get(sg_id2)
                    savegame.highest_dev_province_id = data["highest_dev_province_id"]

    columns += ["victory_points"]
    for data, id in zip(team_data[:-1], team_ids):
        if not VictoryPoint.query.filter_by(mp_id = mp.id, team_id = id, category = institution.value).first():
            vp = VictoryPoint(mp_id = mp.id, team_id = id, category = institution.value, points = data["victory_points"])
            db.session.add(vp)
        else:
            vp = VictoryPoint.query.filter_by(mp_id = mp.id, team_id = id, category = institution.value).first()
            vp.points = data["victory_points"]
    db.session.commit()

    return zip(team_data,team_names,team_colors_hex,team_colors_hsl), columns, header_labels
