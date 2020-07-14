from re import DOTALL, split, compile, findall, search
import numpy as np
import matplotlib.pyplot as plt
from statstool_web import db
from statstool_web.models import *
import datetime


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


def parse_provinces(provinces):
	""" First part of the main parser.
		Parses all province-related information.
		Takes only content from start till end of province information of the savegame.
		Return list of lists with all revelant stats for each province.
		Each Province has its own sub-list with following information (in order):
		[Province_ID, Name, Owner, Tax, Production, Manpower, Development, Trade Node, Culture,
		Religion, Trade Good, Area, Region, Superregion]
		"""
	province_list = split("-\d+=[{]", provinces)[1:]
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

	for province in province_list:
		try:
			result = province_x.search(province).groupdict()
			result["development"] = result["base_tax"] + result["base_production"] + result["base_manpower"]
			result["province_id"] = Province.query.filter_by(name = result["name"]).first().id
			result["trade_good_id"] = TradeGood.query.filter_by(name = result["trade_goods"]).first().id
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

			prov = NationSavegameProvinces(**result)
		except AttributeError as e:
			pass
	db.session.commit()

def parse_wars(content, savegame):
	""" Second part of the main parser. Reads all relevant information about wars
	from the savegame. Returns a list of all wars, as well as a dictionary about
	the participants in each war."""

	previous_wars = content.split("previous_war={")[0].split("active_war={")[1:] + content.split("previous_war={")[1:]
	compile_wars = compile("name=\"(?P<name>.+?)\"\n\thistory", DOTALL)
	compile_participants = compile("value=(?P<participation_score>.+?)\n\t\ttag=\"(?P<nation_tag>.+?)\".+?members={\n\t\t\t\t(?P<losses>[^\n]+)", DOTALL)
	for war in previous_wars:
		result = compile_wars.search(war)
		if result:
			w = War(name = result.group(1), savegame_id = savegame.id)
			db.session.add(w)
			db.session.commit()
		participants = war.split("participants={")[1:]
		if participants:
			for par in participants:
				result = compile_participants.search(par).groupdict()

				result["war_id"] = w.id
				result["participation_score"] = float(result["participation_score"])
				result["losses"] = [int(p) for p in result["losses"].split()]

				result["infantry"] = result["losses"][0] + result["losses"][1]
				w.infantry += result["infantry"]

				result["cavalry"] = result["losses"][3] + result["losses"][4]
				w.cavalry += result["cavalry"]

				result["artillery"] = result["losses"][6] + result["losses"][7]
				w.artillery += result["artillery"]

				result["combat"] = result["losses"][0] + result["losses"][3] + result["losses"][6]
				w.combat += result["combat"]

				result["attrition"] = result["losses"][1] + result["losses"][4] + result["losses"][7]
				w.attrition += result["attrition"]

				result["total"] = result["combat"] + result["attrition"]
				w.total += result["total"]

				del result["losses"]
				war_participant = WarParticipant(**result)
				db.session.add(war_participant)
				w.participants.append(war_participant)
	db.session.commit()


def parse_battles(content, savegame):
	compile_wars = compile("name=\"(?P<name>.+?)\"\n\thistory", DOTALL)

	battles = content.split("\ncombat={")[1]
	battles = battles.split("income_statistics")[0]
	active_wars, *previous_wars = content.split("previous_war={")
	active_wars = active_wars.split("active_war={")[1:]
	total_wars = active_wars + previous_wars

	battle_list = battles.split("battle={")
	battle_regex = compile("""name=\"(?P<province>[^\n]+)\".+?result=(?P<result>[^\n]+).+?
				   attacker=[{](?P<attacker>[^}]+).+?defender=[{](?P<defender>[^}]+).+?
				   """, DOTALL)
	category_regex = lambda string: compile("""cavalry=(?P<{0}_cav>\d+).+?artillery=(?P<{0}_art>\d+).+?
						infantry=(?P<{0}_inf>\d+).+?losses=(?P<{0}_losses>\d+).+?
						country=\"(?P<{0}_tag>[A-Z0-9]{3})\".+?commander=\"(?P<{0}_leader>.+?)\"
					 """.format(string), DOTALL)

	date_list = [datetime.date([int(x) for x in battle_list.pop(0).split("\n")[-2].split("={")[0]])]

	for war in total_wars:
		battle_list = war.split("battle={")[1:]
		for b in battle:
			war_list.append(compile_wars.search(war).group(1))


	for battle, i in zip(battle_list, range(len(battle_list))):
		result = battle_regex.search(battle).groupdict()
		result["date"] = date_list[-1]
		result += category_regex("attacker").search(result["attacker"])
		result += category_regex("defender").search(result["defender"])

		date_list.append(datetime.date([int(x) for x in battle.split("\n")[-2].split("={")[0]]))
	navy_battle_list = []
	army_battle_list = []
	for battle, i in zip(result_list, range(len(result_list))):
		for n in battle[2]:
			battle.append(n)
		del battle[2]
		for n in battle[2]:
			battle.append(n)
		del battle[2]
		try:
			battle.remove("war_goal=3")
		except ValueError:
			pass
		battle.append(war_list[i])
		battle[2] = str(battle[2][0])
	for battle in result_list:
		if ("galley" in battle[3]) or ("light_ship" in battle[3]) or ("heavy_ship" in battle[3]) or (
				"transport" in battle[3]):
			navy_battle_list.append(battle)
		else:
			army_battle_list.append(battle)

	a_list = ["cavalry", "artillery", "infantry", "losses", "country", "commander", "cavalry", "artillery",
			  "infantry", "losses", "country", "commander"]
	n_list = ["galley", "light_ship", "heavy_ship", "transport", "losses", "country", "commander", "galley",
			  "light_ship", "heavy_ship", "transport", "losses", "country", "commander"]
	for battle in army_battle_list:
		if battle[1] == "yes":
			battle[1] = "Attacker"
		else:
			battle[1] = "Defender"
		for i, n in zip(a_list, range(len(a_list))):
			if i in battle[n + 3]:
				battle[n + 3] = battle[n + 3].split("=")[1]
			else:
				battle.insert(n + 3, 0)
		battle[7] = battle[7].split("\"")[1]
		battle[13] = battle[13].split("\"")[1]
		for i, n in zip(battle, range(len(battle))):
			try:
				battle[n] = int(i)
			except ValueError:
				pass
		battle.insert(6, (battle[3] + battle[4] + battle[5]))
		battle.insert(13, (battle[10] + battle[11] + battle[12]))
		battle.insert(17, (battle[6] + battle[13]))
		battle.insert(18, (battle[7] + battle[14]))
	for battle in navy_battle_list:
		if battle[1] == "yes":
			battle[1] = "Attacker"
		else:
			battle[1] = "Defender"
		for i, n in zip(n_list, range(len(n_list))):
			if i in battle[n + 3]:
				battle[n + 3] = battle[n + 3].split("=")[1]
			else:
				battle.insert(n + 3, 0)
		battle[8] = battle[8].split("\"")[1]
		battle[15] = battle[15].split("\"")[1]
		for i, n in zip(battle, range(len(battle))):
			try:
				battle[n] = int(i)
			except ValueError:
				pass
		battle.insert(7, battle[3] + battle[4] + battle[5] + battle[6])
		battle.insert(15, battle[11] + battle[12] + battle[13] + battle[14])
		battle.insert(19, battle[7] + battle[15])
		battle.insert(20, battle[8] + battle[16])

	filtered_army_battle_list = [battle for battle in army_battle_list if battle[17] >= 10000]
	filtered_navy_battle_list = [battle for battle in navy_battle_list if battle[19] >= 10]


def parse_incomestat(content, formable_nations_dict, stats_dict, playertags):
	step = 0
	pbar.reset()
	plabel.setText("Loading Income Data...")

	income_stats = content.split("income_statistics")[1].split("nation_size_statistics")[0]
	country_list = split('\n\tledger_data=[{]\n\t\tname="([A-Z0-9]{3})"\n\t\tdata=[{]\n\t\t\t(.+)\n\t\t[}]\n\t[}]',
						 income_stats)
	income_tag_list, income_info_list = country_list[1:-1:3], country_list[2:-1:3]
	income_x_data = []
	income_y_data = []
	income_dict = {}
	for tag, info in zip(income_tag_list, income_info_list):
		if (tag in stats_dict.keys()) or all_nations_bool:
			income_info_split = info.split()
			income_x_data_set = []
			income_y_data_set = []
			for info in income_info_split:
				info = split("=", info)
				income_x_data_set.append(int(info[0]))
				income_y_data_set.append(int(info[1]))
			income_x_data.append(income_x_data_set)
			income_y_data.append(income_y_data_set)
			income_dict[tag] = [income_x_data_set, income_y_data_set]
			if tag in stats_dict.keys():
				stats_dict[tag]["total_income"] = sum(income_y_data_set)
		step += 1000 / len(income_info_list)
		pbar.setValue(step)
	return income_dict


def parse_trade(content):
	trade_nodes = content.split("trade={")[1].split("tradegoods_total")[0].split("\n\tnode={")[1:]
	trade_regex = "definitions=\"(?P<name>[^\n]+)\".+?local_value=(?P<local>[^\n]+).+?total=(?P<total_power>[^\n]+)"
	trade_regex2 = "top_power={\n\t\t\t\"(?P<power_countries>[^}]+)\"\n\t\t.+?top_power_values={\n\t\t\t(?P<power_values>[^\n]+)"
	trade_regex3 = "current=(?P<value>[^\n]+)"
	compile_trade = compile(trade_regex, DOTALL)
	compile_trade2 = compile(trade_regex2, DOTALL)
	compile_trade3 = compile(trade_regex3)
	trade_stats_list = [[]]

	step = 0
	pbar.reset()
	plabel.setText("Loading Trade Nodes...")

	for node in trade_nodes:
		result = compile_trade.search(node.split("REB")[0])
		if result:
			trade_stats_list.append(list(result.groups()))
		for stats in trade_stats_list[-1]:
			try:
				trade_stats_list[-1][trade_stats_list[-1].index(stats)] = float(stats)
			except (TypeError, ValueError):
				pass
		result = compile_trade2.search(node.split("trade_goods_size")[1])
		if result:
			countries = result.group(1)
			countries = countries.split("\"\n\t\t\t\"")
			power_values = result.group(2)
			power_values = [float(value) for value in power_values.split()]
			country_power_dict = dict(zip(countries, power_values))
			trade_stats_list[-1].append(country_power_dict)
		result = compile_trade3.search(
			node.split("REB")[0])  # seperated from compile_trade because if current = 0, there is no current
		if result:
			trade_stats_list[-1].append(float(result.groups()[0]))
		else:
			trade_stats_list[-1].append(0.0)
		countries = split("\n\t\t}\n\t\t([A-Z0-9]{3})={\n\t\t\t",
						  node.split("\n\t\t}\n\t\tincoming={")[0].split("\n\t\t}\n\t\ttrade_goods_size={")[0])[1:]
		step += 1000 / len(trade_nodes)
		pbar.setValue(step)
	del trade_stats_list[0]
	return trade_stats_list


def compile_main(info, tag, stats_dict):
	main_regex = "\n\t\tdevelopment=(?P<effective_development>\d+.\d+).+?" \
				 "raw_development=(?P<development>\d+.\d+).+?" \
				 "navy_strength=(?P<navy_strength>\d+.\d+).+?estimated_monthly_income=(?P<income>\d+.\d+).+?" \
				 "manpower=(?P<manpower>\d+.\d+).+?max_manpower=(?P<max_manpower>\d+.\d+).+?" \
				 "members=[{]\n\t\t\t\t(?P<losses>[^\n]+)"
	compile_main = compile(main_regex, DOTALL)
	compile_great_power = compile("great_power_score=(?P<great_power_score>\d+.\d+)")
	trade_goods = compile("produced_goods_value={\n(.+)")
	result = compile_main.search(info)
	if result:
		stats_dict[tag] = {}
		stats_dict[tag].update(result.groupdict())
		stats_dict[tag]["losses"] = [int(x) for x in stats_dict[tag]["losses"].split()]
		# 0: Infantry - Combat, 1: Infantry - Attrition, 3: Cavalry - Combat
		# 4: Cavalry - Attrition, 6: Artillery - Combat, 7: Artillery - Combat
		stats_dict[tag]["total_losses"] = sum(stats_dict[tag]["losses"])
		result = compile_great_power.search(info)
		if result:
			stats_dict[tag].update(result.groupdict())
		else:
			stats_dict[tag]["great_power_score"] = 0
		result = trade_goods.search(info)
		if result:
			stats_dict[tag]["trade_goods"] = [float(x) for x in result.group(1).split()]


def compile_techcost(info, tag, tech_dict):
	compile_techcost = compile("technology_cost=(\d+.\d+)")
	compile_techs = compile(
		"""technology={.+?(?P<adm>\d+).+?(?P<dip>\d+).+?(?P<mil>\d+).+?
		active_idea_groups={(?P<idea_groups>[^}]+).+?innovativeness=(?P<innovativeness>\d+.\d+)""", DOTALL)
	result = compile_techcost.search(info)
	if result:
		tech_dict[tag] = {"institution_penalty": round(float(result.group(1)) + 1, 2)}
	else:
		tech_dict[tag] = {"institution_penalty": 1}
	result = compile_techs.search(info)
	if result:
		tech_dict[tag].update(result.groupdict())
		for tech in ("adm","dip","mil"):
			tech_dict[tag][tech] = int(tech_dict[tag][tech])

		tech_dict[tag]["idea_groups"] =\
		{idea.split("=")[0]: int(idea.split("=")[1]) for idea in tech_dict[tag]["idea_groups"].split()}

		tech_dict[tag]["innovativeness"] = float(tech_dict[tag]["innovativeness"])
		tech_dict[tag]["number_of_ideas"] = sum([int(idea.split("=")[1])\
			for idea in result.group(4).split()[1:]])  # Important: Don't count unlocked national ideas
		tech_dict[tag]["tech_score"] = sum([tech_dict[tag][z] for z in ("adm","dip","mil","number_of_ideas")])*\
		(1+tech_dict[tag]["innovativeness"]/200)/tech_dict[tag]["institution_penalty"]
	else:
		del tech_dict[tag]


def compile_color(info, tag, color_dict):
	color_regex = "country_color=[{]\n\t\t\t\t(?P<color>[^\n]+).+?"
	compile_color = compile(color_regex, DOTALL)
	result = compile_color.search(info)
	if result:
		stats = {"country": tag}
		stats.update(result.groupdict())
		color = stats["color"].split()
		for i, n in zip(color, range(len(color))):
			color[n] = int(i)
		hex_color = ("#{0:02x}{1:02x}{2:02x}".format(*color))
		color_dict[stats["country"]] = hex_color


def compile_subjects(info, tag, subject_dict, trade_port_dict):
	compile_subjects = compile("\n\t\tsubjects={([^}]+)}")
	compile_trade_port = compile("trade_port=(.+)")
	result = compile_subjects.search(info)
	if result:
		subject_dict[tag] = [country for country in result.group(1).split()]
	else:
		subject_dict[tag] = []
	trade_port_dict[tag] = int(compile_trade_port.search(info).group(1))


def compile_points_spent(info, tag, stats_dict):
	adm_points_dict, dip_points_dict, mil_points_dict, total_points_dict = {}, {}, {}, {}
	for i in range(48):
		for d in [adm_points_dict, dip_points_dict, mil_points_dict]:
			d[i] = 0;
	try:
		points_spent = info.split("adm_spent_indexed={")[1].split("innovativeness")[0]
		adm, dip, mil = points_spent.split("indexed")
		for cat, dic, string in zip([adm, dip, mil], [adm_points_dict, dip_points_dict, mil_points_dict],
									["adm", "dip", "mil"]):
			cat = findall("\d+=\d+", cat)
			for c in cat:
				key, number = c.split("=")
				dic[int(key)] = int(number)
			total_points_dict[string] = sum(dic.values())
		total_points_dict["total"] = sum(total_points_dict.values())
		total_points_dict["ideas"] = adm_points_dict[0] + dip_points_dict[0] + mil_points_dict[0]
		total_points_dict["tech"] = adm_points_dict[1] + dip_points_dict[1] + mil_points_dict[1]
		total_points_dict["dev"] = adm_points_dict[7] + dip_points_dict[7] + mil_points_dict[7]
		stats_dict[tag]["points_spent"] = [adm_points_dict, dip_points_dict, mil_points_dict, total_points_dict]
	except:
		stats_dict[tag]["points_spent"] = [adm_points_dict, dip_points_dict, mil_points_dict, total_points_dict]


def parse_countries(content, playertags):
	step = 0
	pbar.reset()
	plabel.setText("Loading Country Data...")
	countries = split("\n\t([A-Z0-9]{3})", content.split("\ncountries={")[1].split('active_advisors')[0])
	tag_list, info_list = countries[1:-1:2], countries[2:-1:2]
	sorted_tag_list = sorted(tag_list)

	stats_dict, color_dict, subject_dict, trade_port_dict, tech_dict = {}, {}, {}, {}, {}

	for info, tag in zip(info_list, tag_list):
		if (tag in playertags) or all_nations_bool:
			compile_main(info, tag, stats_dict)
		if tag in stats_dict.keys():
			compile_techcost(info, tag, tech_dict)
			compile_player = compile("was_player=yes")
			compile_color(info, tag, color_dict)
			compile_subjects(info, tag, subject_dict, trade_port_dict)
			compile_points_spent(info, tag, stats_dict)
		step += 1000 / len(tag_list)
		pbar.setValue(step)
	cleanup_data(stats_dict, tech_dict)
	return stats_dict, sorted_tag_list, subject_dict, color_dict, trade_port_dict, tech_dict


def cleanup_data(stats_dict, tech_dict):
	for tag in stats_dict.keys():
		for entry_name in stats_dict[tag].keys():
			try:
				stats_dict[tag][entry_name] = float(stats_dict[tag][entry_name])
			except (ValueError, TypeError):
				pass
		stats_dict[tag]["manpower"] = int(1000 * stats_dict[tag]["manpower"])
		stats_dict[tag]["max_manpower"] = int(1000 * stats_dict[tag]["max_manpower"])
		stats_dict[tag]["great_power_score"] = \
			round(int(stats_dict[tag]["great_power_score"]) * (tech_dict[tag]["institution_penalty"]))


def compile_monarchs(tag, country, monarch_list, monarch_id):
	compile_monarch_info = compile(
		"id={\n.+?id=" + monarch_id + ".+?name=\"(.+?)\".+?DIP=(\d).+?ADM=(\d).+?MIL=(\d).+?",
		DOTALL)
	result = compile_monarch_info.search(country.split("original_capital")[0])
	if result:
		temp = [int(i) for i in result.groups()[1:]]
		result = [tag] + list(result.groups()) + [sum(temp)]
		monarch_list.append(result)


def parse_history(content, stats_dict):
	countries = split("\n\t([A-Z0-9]{3})", content.split("\ncountries={")[1].split('active_advisors')[0])
	tag_list, info_list = countries[1:-1:2], countries[2:-1:2]
	compile_monarch_id = compile("\tmonarch={\n\t\t\tid=(\d+)")
	compile_previous_monarchs_id = compile("\tprevious_monarch={\n\t\t\tid=(\d+)")
	monarch_list = []
	for tag, country in zip(tag_list, info_list):
		if tag in stats_dict.keys():
			result1 = compile_previous_monarchs_id.findall(country)
			result2 = compile_monarch_id.search(country)
			if result1:
				for monarch in result1:
					compile_monarchs(tag, country, monarch_list, monarch)
			if result2:
				compile_monarchs(tag, country, monarch_list, result2.group(1))
	return monarch_list

def parse(savegame):
	with open(savegame.file, 'r', encoding = 'cp1252') as sg:
		content = sg.read()
		provinces = content.split("\nprovinces={")[1].split("countries={")[0]
		savegame.year = int(search("date=(?P<year>\d{4})", content).group(1))
		total_trade_goods = list(findall("tradegoods_total_produced={\n(.+)", content)[0].split())
		i = 0
		for value in total_trade_goods:
			tg = TotalGoodsProduced(savegame_id = savegame.id, trade_good_id = i, amount = value)
			db.session.add(tg)
			i += 1

		parse_provinces(provinces)
		parse_wars(content, savegame)
		parse_battles(content, savegame)
		stats_dict, sorted_tag_list, subject_dict, color_dict, \
		trade_port_dict, tech_dict = parse_countries(content, playertags)
		income_dict = parse_incomestat(content, formable_nations_dict, stats_dict, playertags)
		trade_stats_list = parse_trade(content)
		monarch_list = parse_history(content, stats_dict)
	return stats_dict, year, total_trade_goods, sorted_tag_list, income_dict,\
		color_dict, army_battle_list, navy_battle_list, province_stats_list,\
		trade_stats_list, subject_dict, trade_port_dict,\
		war_list, war_dict, tech_dict, monarch_list
