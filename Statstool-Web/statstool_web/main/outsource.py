from statstool_web.models import VictoryPoints


def mp2_data(nation_tags, mp_id):
    header_labels = ["Nation", "Basis", "Kriege", "Kolonialismus", "Druckerpresse", \
    "Globaler Handel", "Manufakturen", "Aufklärung", "Industrialisierung", \
    "erster Spielerkrieg-Sieger", "erste Weltumseglung", "Armee-Professionalität", \
    "Großmacht", "Hegemonie", "Gesamt"]

    data = {}
    for tag in nation_tags:
        data[tag] = [2] + [0]*(len(header_labels)-3)

    institutions = ("colonialism", "printing_press", "global_trade", "manufactories", "enlightenment","industrialization")

    for institution, column in zip(institutions, range(2,8)):
        for tag in nation_tags:
            if (result := VictoryPoints.query.filter_by(mp_id = mp_id, institution = institution, nation_tag = tag).first()):
                data[tag][column] = result.victory_points

    #erster Spielerkrieg
    #data["D00"][8] = 1

    #global_trade
    data["D05"][4] += 2

    return header_labels, data


def mp1_data():
    header_labels = ["Nation", "Basis", "Kriege", "Renaissance", "Kolonialismus", "Druckerpresse", "Globaler Handel", "Manufakturen", "Aufklärung", "Industrialisierung", "Gesamt"]

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

    return header_labels, data
