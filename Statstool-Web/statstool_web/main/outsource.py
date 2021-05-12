from statstool_web.models import *
from math import ceil

def get_nation_info(savegame):
    nation_tags = [x.tag for x in savegame.player_nations]
    nation_names = [NationSavegameData.query.filter_by(
        savegame_id=savegame.id, nation_tag=tag).first().nation_name for tag in nation_tags]
    nation_colors_hex = [NationSavegameData.query.filter_by(nation_tag=tag,
                                                            savegame_id=savegame.id).first().color for tag in nation_tags]
    nation_colors_hsl = [NationSavegameData.query.filter_by(nation_tag=tag,
                                                            savegame_id=savegame.id).first().color.hsl for tag in nation_tags]
    return zip(nation_names, nation_tags, nation_colors_hex, nation_colors_hsl)


def mp3_data(mp_id, savegame):
    institutions = ("colonialism", "printing_press", "global_trade",
                "manufactories", "enlightenment", "industrialization")
    
    payload = {"mp_id": mp_id, "current_mp": MP.query.get(mp_id)}
    payload["header_labels"] = ["Team", "Provinzen", "Kolonialismus", "Druckerpresse",
                             "Globaler Handel", "Manufakturen", "Aufklärung", "Industrialisierung",
                             "erster Spielerkrieg-Sieger", "Globaler Handel-Sieger", "Gesamt"]
    payload["num_columns"] = len(payload["header_labels"])

    two_vp_province_ids = {382: "Damaskus", 227: "Lissabon", 333: "Majorca",
                            1765: "Sofia", 177: "Maine", 45: "Lübeck", 257: "Warschau", 295: "Moskau"}

    one_vp_province_ids = {361: "Kairo", 223: "Granada", 151: "Konstantinopel",
                            341: "Tunis", 231: "Porto", 170: "Finistère", 183: "Paris", 50: "Berlin",
                            153: "Pest", 1756: "Bessarabien", 4142: "Ostjylland", 41: "Königsberg"}
    
    free_provinces_one_vp = [x for x in one_vp_province_ids.values()]
    free_provinces_two_vp = [x for x in two_vp_province_ids.values()]

    teams = sorted(MP.query.get(mp_id).teams, key = lambda team: team.id)
    team_names = []
    for team in teams:
        team_names.append("Team {}".format(team.id))
    team_colors_hex = ["#ffffff"]*len(teams)
    team_colors_hsl = [(0, 0, 100)]*len(teams)
    team_ids = [team.id for team in teams]
    payload["nation_info"] = zip(team_names, team_ids, team_colors_hex, team_colors_hsl)

    data = {}
    for team in teams:
        data[team.id] = [0]*(len(payload["header_labels"])-2)

    for institution, column in zip(institutions, range(1, 7)):
        for team in teams:
            if (result := VictoryPoint.query.filter_by(mp_id=mp_id, category=institution, team_id=team.id).first()):
                data[team.id][column] = result.points

    province_points_dict = {}

    for team in teams:
        if (vp := VictoryPoint.query.filter_by(mp_id=mp_id, team_id=team.id, category="provinces").first()):
            vp.points = 0
            province_points_dict[team.id] = vp
        else:
            vp = VictoryPoint(mp_id=mp_id, team_id=team.id,
                                category="provinces", points=0)
            db.session.add(vp)
            province_points_dict[team.id] = vp
    
    team_province_dict = {team.id: [[], []] for team in teams}

    for (id, name) in two_vp_province_ids.items():
        ProviceData = NationSavegameProvinces.query.filter_by(
            savegame_id=savegame.id, province_id=id).first()
        owner = ProviceData.nation_tag
        for team in teams:
            if owner in (team.team_tag1, team.team_tag2):
                province_points_dict[team.id].points += 2
                team_province_dict[team.id][0].append(name)
                free_provinces_two_vp.remove(name)

    for (id, name) in one_vp_province_ids.items():
        ProviceData = NationSavegameProvinces.query.filter_by(
            savegame_id=savegame.id, province_id=id).first()
        owner = ProviceData.nation_tag
        for team in teams:
            if owner in (team.team_tag1, team.team_tag2):
                province_points_dict[team.id].points += 1
                team_province_dict[team.id][1].append(name)
                free_provinces_one_vp.remove(name)

    db.session.commit()
    payload["num_free_rows"] = max([ceil(len(free_provinces_one_vp)/3), ceil(len(free_provinces_two_vp)/3)])
    payload["free_provinces_one_vp"] = free_provinces_one_vp
    payload["free_provinces_two_vp"] = free_provinces_two_vp
    payload["team_province_dict"] = team_province_dict

    for team in teams:
        data[team.id][0] = VictoryPoint.query.filter_by(
            mp_id=mp_id, team_id=team.id, category="provinces").first().points
        vp = VictoryPoint.query.filter_by(
            mp_id=mp_id, team_id=team.id, category="first_player_war").first()
        if vp:
            data[team.id][-2] = vp.points
        vp = VictoryPoint.query.filter_by(
            mp_id=mp_id, team_id=team.id, category="global_trade_spawn").first()
        if vp:
            data[team.id][-1] = vp.points
        data[team.id].append(sum(data[team.id]))

    payload["data"] = data

    
    return payload

def mp2_data(mp_id, savegame):
    payload = {"mp_id": mp_id, "current_mp": MP.query.get(mp_id)}
    payload["header_labels"] = ["Nation", "Basis", "Kriege", "Kolonialismus", "Druckerpresse", \
    "Globaler Handel", "Manufakturen", "Aufklärung", "Industrialisierung", \
    "erster Spielerkrieg-Sieger", "erste Weltumseglung", "Armee-Professionalität", \
    "Großmacht", "Hegemonie", "Gesamt"]
    payload["num_columns"] = len(payload["header_labels"])

    data = {}
    nation_tags = [x.tag for x in savegame.player_nations]
    for tag in nation_tags:
        data[tag] = [2] + [0]*(len(payload["header_labels"])-3)

    institutions = ("colonialism", "printing_press", "global_trade", "manufactories", "enlightenment","industrialization")

    for institution, column in zip(institutions, range(2,8)):
        for tag in nation_tags:
            if (result := VictoryPoints.query.filter_by(mp_id = mp_id, institution = institution, nation_tag = tag).first()):
                data[tag][column] = result.victory_points

    #erster Spielerkrieg
    #data["D00"][8] = 1

    #global_trade
    data["D05"][4] += 2

    #great_power
    data["MPK"][11] = 1

    #army_prof

    data["D03"][10] = 2

    #hegemony

    data["MPK"][12] = 2
    data["D05"][12] = 2
    data["D08"][12] = 1

    #wars

    data["D03"][1] = 1
    data["MPK"][1] = 1

    data["D02"][1] = -1
    data["D07"][1] = -1

    for tag in data.keys():
        data[tag].append(sum(data[tag]))

    payload["data"] = data

    return payload


def mp1_data():
    payload = {"mp_id": mp_id, "current_mp": MP.query.get(mp_id)}

    payload["header_labels"] = ["Nation", "Basis", "Kriege", "Renaissance", "Kolonialismus", \
        "Druckerpresse", "Globaler Handel", "Manufakturen", "Aufklärung", "Industrialisierung", "Gesamt"]
    payload["num_columns"] = len(payload["header_labels"])

    data = {}

    data["SPA"] = [2,0,0,0,0,0,0,0,0]
    data["FRA"] = [2,-2,0,0,0,0,0,0,0]
    data["GBR"] = [2,-2,0,2,3,2,0,0,0]
    data["NED"] = [2,2,0,0,0,1,1,3,0]
    data["HAB"] = [2,4,0,0,0,0,3,1,0]
    data["SWE"] = [2,-2,0,0,0,0,0,0,0]
    data["PLC"] = [2,-1,0,0,0,0,0,1,0]
    data["TUR"] = [1,-3,2,1,1,2,2,0,0]
    data["RUS"] = [1,4,0,0,1,1,0,1,0]

    for tag in data.keys():
        data[tag].append(sum(data[tag]))
    
    payload["data"] = data

    return payload
