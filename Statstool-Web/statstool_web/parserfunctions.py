from re import DOTALL, split, compile, findall, search
import numpy as np
import matplotlib.pyplot as plt
from statstool_web import db
from statstool_web.models import *
from sqlalchemy.exc import IntegrityError
import datetime
from colour import Color


def colormap(values, mode=0, output_range=1):
	""" Green - Red Colormap with min, max & mean
		Takes list of values, 0,1,2 to specify mode and the output_range (1, 255 mainly) as input.
		Mode 0: Colormap with Min - Median - Max
		Mode 1: Colormap with (Min - ) Median - Max, 0 is always yellow.
		Mode 2: Colors reversed: Green is min, red is max
		Returns rgb color-values in range (0,1). """

	values = [float(v) for v in values]
	mini = min(values)
	maxi = max(values)
	if mode == 1 and mini < 0:
		# if both positive and negative values are present, set median to 0.
		median = 0
	else:
		median = np.median(values)
	if (mini != median) and (median != maxi):
		normal1 = plt.Normalize(mini, median, clip=True)
		normal2 = plt.Normalize(median, maxi, clip=True)
		normal = (normal1(values) + normal2(values)) / 2
	else:
		normal = plt.Normalize(mini, maxi, clip=True)(values)
	color_values = []
	for n in normal:
		b = 0
		if mode == 0:
			r = (1 - n) * output_range
			g = n * output_range

		if mode == 1:
			r = ((1 - n) / 2) * output_range
			g = (n / 2 + 0.5) * output_range

		if mode == 2:
			r = n * output_range
			g = (1 - n) * output_range

		color_values.append((r, g, b))
	return color_values


def edit_parse(filename):
	""" Pre-Parser: Parsing player nations and real (alive) nations
		in order to enable dynamic nation selection.
		Returns list of Player-Nations-Tag and list of all real nations tag in alphabetical order. """

	with open(filename, 'r', encoding = 'cp1252') as sg:
		content = sg.read()
		compile_player = compile("was_player=yes")
		compile_real_nations = compile("\n\t\tdevelopment")  # Dead nations don't have development
		countries = split("\n\t([A-Z0-9]{3})", content.split("\ncountries={")[1].split('active_advisors')[0])
		tag_list, info_list = countries[1:-1:2], countries[2:-1:2]
		playertag_list = []
		real_nations_list = []

		for info, tag in zip(info_list, tag_list):
			result = compile_real_nations.search(info)
			if result:
				real_nations_list.append(tag)
				result = compile_player.search(info)
				if result:
					playertag_list.append(tag)

	return playertag_list, sorted(real_nations_list)


def parse_provinces(provinces, savegame):
	""" First part of the main parser.
		Parses all province-related information.
		Takes only content from start till end of province information of the savegame.
		Return list of lists with all revelant stats for each province.
		Each Province has its own sub-list with following information (in order):
		[Province_ID, Name, Owner, Tax, Production, Manpower, Development, Trade Node, Culture,
		Religion, Trade Good, Area, Region, Superregion]
		"""
	provinces = split("-(\d+)=[{]", provinces)[1:]
	province_id_list = provinces[::2]
	province_list = provinces[1::2]
	for province, x in zip(province_list, range(len(province_list))):
		province_list[x] = province.split("history")[0]
		province_list[x] += province.split("discovered_by=")[-1]

	province_regex = "name=\"(?P<name>[^\n]+)\".+?" \
					 "base_tax=(?P<base_tax>\d+).+?" \
					 "base_production=(?P<base_production>\d+).+?base_manpower=(?P<base_manpower>\d+).+?" \
					 "trade_goods=(?P<trade_goods>[^\n]+)"
	province_regex2 = "owner=\"(?P<owner>[^\n]+)\""  # Seperated from main regex, because uncolonized provinces don't have a owner.
	province_regex3 = "religion=(?P<religion>[^\n]+)"  # Because some provinces have no fucking religion!
	province_regex4 = "culture=(?P<culture>[^\n]+)"  # Because some provinces have no fucking culture!
	province_regex5 = "trade_power=(?P<trade_power>[^\n]+)"
	province_x = compile(province_regex, DOTALL)
	province_x2 = compile(province_regex2, DOTALL)
	province_x3 = compile(province_regex3, DOTALL)
	province_x4 = compile(province_regex4, DOTALL)
	province_x5 = compile(province_regex5, DOTALL)

	try:
		i = -1
		for province, id in zip(province_list,province_id_list):
			try:
				result = province_x.search(province).groupdict()
				for cat in ("base_tax", "base_production", "base_manpower"):
					result[cat] = int(result[cat])
				result["development"] = result["base_tax"] + result["base_production"] + result["base_manpower"]
				result["province_id"] = id
				result["savegame_id"] = savegame.id
				trade_good = TradeGood.query.filter_by(name = result["trade_goods"]).first()
				if trade_good:
					result["trade_good_id"] = trade_good.id
				del result["name"], result["trade_goods"]

				owner = province_x2.search(province)
				if owner:
					result["nation_tag"] =  owner.group(1)

				religion = province_x3.search(province)
				if religion:
					result["religion"] = religion.group(1)

				culture = province_x4.search(province)
				if culture:
					result["culture"] = culture.group(1)

				trade_power = province_x5.search(province)
				if trade_power:
					result["trade_power"] = float(trade_power.group(1))

				prov = SavegameProvinces(**result)
				db.session.add(prov)
			except AttributeError as e:
				pass
			db.session.flush()
			i -= 1
	except IntegrityError as e:
		print(e)
		db.session.rollback()
	else:
		db.session.commit()


def parse_wars(content, savegame):
	""" Second part of the main parser. Reads all relevant information about wars
	from the savegame. Returns a list of all wars, as well as a dictionary about
	the participants in each war."""

	active_wars, *previous_wars = content.split("previous_war={")
	active_wars = active_wars.split("active_war={")[1:]
	total_wars = active_wars + previous_wars

	war_name = compile("name=\"(?P<name>.+?)\"", DOTALL)
	compile_participants = compile("value=(?P<participation_score>.+?)\n\t\ttag=\"(?P<nation_tag>.+?)\".+?members={\n\t\t\t\t(?P<losses>[^\n]+)", DOTALL)
	battle_regex = compile("name=\"(?P<province>.+?)\".+?result=(?P<result>[^\n]+).+?"\
				"attacker=[{](?P<attacker>[^}]+).+?defender=[{](?P<defender>[^}]+).+?", DOTALL)

	for war in total_wars:
		result = war_name.search(war)
		if result:
			w = War(name = result.group(1), infantry = 0, cavalry = 0, artillery = 0, combat = 0, attrition = 0, total = 0)
			savegame.wars.append(w)
			if war in active_wars:
				w.ongoing = True
			else:
				w.ongoing = False

			battle_list = war.split("battle={")

			if len(battle_list) > 1:
				date_list = [datetime.date(*[int(x) for x in battle_list[0].split("\n")[-2].split("={")[0].split(".")])]

				for battle in battle_list[1:]:
					parse_battle(battle, w, date_list, battle_regex, savegame)

				participants = war.split("participants={")[1:]
				for p in participants:
					parse_war_participants(p, compile_participants, w)

			db.session.add(w)


def parse_battle(battle, war, date_list, battle_regex, savegame):
	result = battle_regex.search(battle)
	battle_dict = result.groupdict()
	battle_dict["date"] = date_list[-1]
	for role in ("attacker", "defender"):
		battle_dict.update({"{0}_{1}".format(role, line.split("=")[0].split()[0]): line.split("=")[1].replace('"','') \
							for line in battle_dict[role].split("\n")[1:-1] \
							if line.split("=")[0].split()[0] != "war_goal"})

	del battle_dict["attacker"], battle_dict["defender"]

	for key in battle_dict.keys():
		try:
			battle_dict[key] = int(battle_dict[key])
		except (ValueError, TypeError):
			pass

	if sum([x in battle_dict.keys() for x in ("attacker_infantry", "attacker_cavalry", "attacker_artillery")]) > 0:
		for role in ("attacker", "defender"):
			battle_dict["{0}_total".format(role)] = sum([battle_dict[x] for x in ("{0}_infantry".format(role), "{0}_cavalry".format(role), "{0}_artillery".format(role)) if x in battle_dict.keys()])
		battle_dict["total_combatants"] = battle_dict["attacker_total"] + battle_dict["defender_total"]
		battle_dict["total_losses"] = battle_dict["attacker_losses"] + battle_dict["defender_losses"]

		b = ArmyBattle(**battle_dict)
		war.army_battles.append(b)
		savegame.army_battles.append(b)
	else:
		b = NavyBattle(**battle_dict)
		war.navy_battles.append(b)
		savegame.navy_battles.append(b)

	db.session.add(b)

	if battle.split("\n")[-2] != "}":
		date_list.append(datetime.date(*[int(x) for x in battle.split("\n")[-2].split("={")[0].split(".")]))


def parse_war_participants(participant, compile_participants, war):
	result = compile_participants.search(participant).groupdict()

	result["participation_score"] = float(result["participation_score"])
	result["losses"] = [int(p) for p in result["losses"].split()]

	result["infantry"] = result["losses"][0] + result["losses"][1]
	war.infantry += result["infantry"]

	result["cavalry"] = result["losses"][3] + result["losses"][4]
	war.cavalry += result["cavalry"]

	result["artillery"] = result["losses"][6] + result["losses"][7]
	war.artillery += result["artillery"]

	result["combat"] = result["losses"][0] + result["losses"][3] + result["losses"][6]
	war.combat += result["combat"]

	result["attrition"] = result["losses"][1] + result["losses"][4] + result["losses"][7]
	war.attrition += result["attrition"]

	result["total"] = result["combat"] + result["attrition"]
	war.total += result["total"]

	del result["losses"]
	war_participant = WarParticipant(**result)
	war.participants.append(war_participant)
	db.session.add(war_participant)


def compile_main(info, tag, savegame, main, side_regex_dict, tech_cost, tech):

	result = main.search(info)
	if result:
		nation_data = result.groupdict()
		nation_data["nation_tag"] = tag
		nation_data["savegame_id"] = savegame.id
		nation_data["manpower"] = int(nation_data["manpower"].replace(".",""))
		nation_data["max_manpower"] = int(nation_data["max_manpower"].replace(".",""))
		nation_data["development"] = int(float(nation_data["development"]))
		color = [int(x) for x in nation_data["color"].split()]
		hex_color = Color("#{0:02x}{1:02x}{2:02x}".format(*color))
		nation_data["color"] = hex_color

		for float_column in ("effective_development","navy_strength","income"):
			nation_data[float_column] = float(nation_data[float_column])

		for category, regex in side_regex_dict.items():
			result = regex.search(info)
			if result:
				nation_data[category] = result.group(1)
			else:
				nation_data[category] = 0

		compile_army_losses(info, tag, savegame, nation_data)
		compile_tech(info, tag, savegame, nation_data, tech_cost, tech)

		nation_data["great_power_score"] = round(int(float(nation_data["great_power_score"])) * (nation_data["institution_penalty"]))

		return nation_data

def compile_army_losses(info, tag, savegame, nation_data):

	# 0: Infantry - Combat, 1: Infantry - Attrition, 3: Cavalry - Combat
	# 4: Cavalry - Attrition, 6: Artillery - Combat, 7: Artillery - Combat

	temp = [int(x) for x in nation_data["losses"].split()]
	del nation_data["losses"]

	nation_losses = {"nation_tag": tag, "savegame_id": savegame.id}
	nation_losses["infantry"] = temp[0] + temp[1]
	nation_losses["cavalry"] = temp[3] + temp[4]
	nation_losses["artillery"] = temp[6] + temp[7]
	nation_losses["combat"] = temp[0] + temp[3] + temp[6]
	nation_losses["attrition"] = temp[1] + temp[4] + temp[7]
	nation_losses["total"] = sum(temp)
	nation_losses["color"] = nation_data["color"]

	nl = NationSavegameArmyLosses(**nation_losses)
	db.session.add(nl)


def compile_tech(info, tag, savegame, nation_data, tech_cost, tech):

	result = tech_cost.search(info)
	if result:
		nation_data["institution_penalty"] = round(float(result.group(1)) + 1, 2)
	else:
		nation_data["institution_penalty"] = 1

	result = tech.search(info)
	if result:
		nation_data.update(result.groupdict())
		for category in ("adm_tech","dip_tech","mil_tech"):
			nation_data[category] = int(nation_data[category])

		nation_data["idea_groups"] =\
		{idea.split("=")[0]: int(idea.split("=")[1]) for idea in nation_data["idea_groups"].split()}

		nation_data["innovativeness"] = float(nation_data["innovativeness"])
		nation_data["number_of_ideas"] = sum([int(idea.split("=")[1])\
			for idea in result.group(4).split()[1:]])  # Important: Don't count unlocked national ideas
		del nation_data["idea_groups"]


def compile_goods_produced(info, tag, savegame, trade_goods):

	result = trade_goods.search(info)
	if result:
		i = 0
		for goods_produced in [float(x) for x in result.group(1).split()]:
			gp = NationSavegameGoodsProduced(nation_tag = tag, savegame_id = savegame.id,
							trade_good_id = i, amount = goods_produced)
			db.session.add(gp)
			i += 1


def compile_points_spent(info, tag, savegame):

	for category in ("adm", "dip", "mil"):
		if f"{category}_spent_indexed" in info:
			points_spent = info.split(f"{category}_spent_indexed")[1].split("}")[0]
			results = findall("\d+=\d+", points_spent)
			for result in results:
				key, value = result.split("=")
				ps = NationSavegamePointsSpent(nation_tag = tag, savegame_id = savegame.id,
						points_spent_id = int(key), points_spent_category = category, amount = int(value))
				db.session.add(ps)


def parse_history(info, tag, savegame, monarch_id, previous_monarchs_id):
	result1 = previous_monarchs_id.findall(info)
	result2 = monarch_id.search(info)
	if result1:
		for monarch in result1:
			compile_monarchs(info, tag, savegame, monarch)
	if result2:
		compile_monarchs(info, tag, savegame, result2.group(1))


def parse_relations(info, tag, ae, ae_dict):
	relations = split("([A-Z0-9]{3})={",info.split("active_relations={")[1].split("decision_seed")[0])
	if relations:
		relation_tag_list, relation_info_list = relations[1:-1:2], relations[2:-1:2]
		for rel_tag, rel_info in zip(relation_tag_list, relation_info_list):
			result = ae.search(rel_info)
			if result:
				n = -float(result.group(1))
				if rel_tag in ae_dict.keys():
					if n > ae_dict[rel_tag]:
						ae_dict[rel_tag] = n
				else:
					ae_dict[rel_tag] =  n


def parse_regiments(info, tag, regiment_strength, nation_data):
	regiment_data = split("regiment={",info)[1:]
	standing_army = 0
	for regiment in regiment_data:
		result = regiment_strength.search(regiment)
		if result:
			standing_army += float(result.group(1))*1000
		else:
			standing_army += 1000
	nation_data["standing_army"] = standing_army

def parse_ships(info, tag, nation_data):
	with open("../Statstool-Web/files/ship_cannons.txt", "r") as file:
		ship_cannons_dict = eval(file.read())
	ship_type = compile('type="(.+?)"')
	ship_data = split("ship={",info)[1:]
	navy_cannons = 0
	for ship in ship_data:
		result = ship_type.search(ship)
		if result:
			unit_type = result.group(1)
			if unit_type in ship_cannons_dict.keys():
				navy_cannons += ship_cannons_dict[unit_type]
			else:
				print("HILFE:{0}!".format(unit_type))

	nation_data["navy_cannons"] = navy_cannons


def compile_monarchs(info, tag, savegame, monarch_id):
	monarch_info = compile(
		"id={\n.+?id=" + monarch_id + ".+?name=\"(?P<name>.+?)\".+?DIP=(?P<dip>\d).+?ADM=(?P<adm>\d).+?MIL=(?P<mil>\d).+?",
		DOTALL)
	result = monarch_info.search(info)
	if result:
		payload = result.groupdict()
		for category in ("adm", "dip", "mil"):
			payload[category] = int(payload[category])
		payload["nation_tag"] = tag
		payload["savegame_id"] = savegame.id
		monarch = Monarch(**payload)
		db.session.add(monarch)


def parse_countries(content, savegame):
	countries = split("\n\t([A-Z0-9]{3})", content.split("\ncountries={")[1].split('active_advisors')[0])
	tag_list, info_list = countries[1:-1:2], countries[2:-1:2]
	sorted_tag_list = sorted(tag_list)

	main = compile("\n\t\tdevelopment=(?P<effective_development>\d+.\d+).+?" \
				 "raw_development=(?P<development>\d+.\d+).+?country_color=[{]\n\t\t\t\t(?P<color>[^\n]+).+?" \
				 "navy_strength=(?P<navy_strength>\d+.\d+).+?estimated_monthly_income=(?P<income>\d+.\d+).+?" \
				 "manpower=(?P<manpower>\d+.\d+).+?max_manpower=(?P<max_manpower>\d+.\d+).+?" \
				 "members=[{]\n\t\t\t\t(?P<losses>[^\n]+)", DOTALL)

	great_power = compile("great_power_score=(\d+.\d+)")
	num_converted_religion = compile("num_converted_religion=(\d+)")
	num_of_colonies = compile("num_of_colonies=(\d+)")
	side_regex_dict = {"great_power_score": great_power, "num_converted_religion": num_converted_religion, "num_of_colonies": num_of_colonies}

	tech_cost = compile("technology_cost=(\d+.\d+)")
	tech = compile("technology={.+?(?P<adm_tech>\d+).+?(?P<dip_tech>\d+).+?(?P<mil_tech>\d+).+?"\
			"active_idea_groups={(?P<idea_groups>[^}]+).+?innovativeness=(?P<innovativeness>\d+.\d+)", DOTALL)
	trade_goods = compile("produced_goods_value={\n(.+)")
	monarch_id = compile("\tmonarch={\n\t\t\tid=(\d+)")
	previous_monarchs_id = compile("\tprevious_monarch={\n\t\t\tid=(\d+)")
	ae = compile("modifier=\"aggressive_expansion\"[^}]+?current_opinion=(-\d+.\d+)", DOTALL)
	regiment_strength = compile("strength=(\d.\d+)")

	ae_dict = {}
	for info, tag in zip(info_list, tag_list):
		nation_data = compile_main(info, tag, savegame, main, side_regex_dict, tech_cost, tech)
		if nation_data:
			compile_goods_produced(info, tag, savegame, trade_goods)
			compile_points_spent(info, tag, savegame)
			parse_history(info, tag, savegame, monarch_id, previous_monarchs_id)
			parse_relations(info, tag, ae, ae_dict)
			parse_regiments(info, tag, regiment_strength, nation_data)
			parse_ships(info, tag, nation_data)
			nd = NationSavegameData(**nation_data)
			db.session.add(nd)

	for tag in tag_list:
		nation = NationSavegameData.query.filter_by(nation_tag = tag, savegame_id = savegame.id).first()
		if tag in ae_dict.keys():
			nation.highest_ae = ae_dict[tag]

def parse_incomestat(content, savegame):

	income_stats = content.split("income_statistics")[1].split("nation_size_statistics")[0]
	country_list = split('\n\tledger_data=[{]\n\t\tname="([A-Z0-9]{3})"\n\t\tdata=[{]\n\t\t\t(.+)\n\t\t[}]\n\t[}]',
						 income_stats)
	income_tag_list, income_info_list = country_list[1:-1:3], country_list[2:-1:3]
	for tag, info in zip(income_tag_list, income_info_list):
		income_info_split = info.split()
		for info in income_info_split:
			year, value = split("=", info)
			income_year = NationSavegameIncomePerYear(nation_tag = tag, savegame_id = savegame.id,
							year = int(year), amount = int(value))
			db.session.add(income_year)


def parse_trade(content):
	trade_nodes = content.split("trade={")[1].split("tradegoods_total")[0].split("\n\tnode={")[1:]
	trade1 = compile("definitions=\"(?P<name>[^\n]+)\".+?local_value=(?P<local>[^\n]+).+?total=(?P<total_power>[^\n]+)", DOTALL)
	trade2 = compile("top_power={\n\t\t\t\"(?P<power_countries>[^}]+)\"\n\t\t.+?top_power_values={\n\t\t\t(?P<power_values>[^\n]+)", DOTALL)
	trade3 = compile("current=(?P<value>[^\n]+)")

	for node in trade_nodes:
		result = trade1.search(node.split("REB")[0])
		if result:
			trade_stats_list.append(list(result.groups()))
		for stats in trade_stats_list[-1]:
			try:
				trade_stats_list[-1][trade_stats_list[-1].index(stats)] = float(stats)
			except (TypeError, ValueError):
				pass
		result = trade2.search(node.split("trade_goods_size")[1])
		if result:
			countries = result.group(1)
			countries = countries.split("\"\n\t\t\t\"")
			power_values = result.group(2)
			power_values = [float(value) for value in power_values.split()]
			country_power_dict = dict(zip(countries, power_values))
			trade_stats_list[-1].append(country_power_dict)
		result = trade3.search(node.split("REB")[0])  # seperated from compile_trade because if current = 0, there is no current
		if result:
			trade_stats_list[-1].append(float(result.groups()[0]))
		else:
			trade_stats_list[-1].append(0.0)
		countries = split("\n\t\t}\n\t\t([A-Z0-9]{3})={\n\t\t\t",
						  node.split("\n\t\t}\n\t\tincoming={")[0].split("\n\t\t}\n\t\ttrade_goods_size={")[0])[1:]
	del trade_stats_list[0]


def parse(savegame):
	with open(savegame.file, 'r', encoding = 'cp1252') as sg:
		content = sg.read()
		provinces = content.split("\nprovinces={")[1].split("countries={")[0]
		savegame.year = int(search("date=(?P<year>\d{4})", content).group(1))
		total_trade_goods = list(findall("tradegoods_total_produced={\n(.+)", content)[0].split())
		i = 0

		try:
			for value in total_trade_goods:
				tg = TotalGoodsProduced(savegame_id = savegame.id, trade_good_id = i, amount = value)
				db.session.add(tg)
				i += 1
			db.session.flush()

			parse_provinces(provinces, savegame)
			print("Provinzen Done")
			parse_wars(content, savegame)
			print("Kriege Done")
			parse_countries(content, savegame)
			print("Länder Done")
			parse_incomestat(content, savegame)
			print("Einkommen-Stats Done")
			#parse_trade(content)
			db.session.flush()
		except IntegrityError:
			db.session.rollback()
		else:
			savegame.parse_flag = True
			db.session.commit()
