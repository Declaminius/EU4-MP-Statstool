from re import DOTALL, split, compile, findall
import numpy as np
import matplotlib.pyplot as plt


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

	with open(filename, 'r') as sg:
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


def parse_regions_files(filename):
	"""	 Reads data about areas, regions and superregion from
			another file, which contains the already parsed input. """
	with open(filename, "r") as sg:
		data = eval(sg.read())
	return data


def parse_provinces(provinces, pbar, plabel):
	""" First part of the main parser.
		Parses all province-related information.
		Takes only content from start till end of province information of the savegame.
		Return list of lists with all revelant stats for each province.
		Each Province has its own sub-list with following information (in order):
		[Province_ID, Name, Owner, Tax, Production, Manpower, Development, Trade Node, Culture,
		Religion, Trade Good, Area, Region, Superregion]
		"""
	step = 0
	plabel.setText("Loading Province Data...")

	id_index_dict = {}
	area_dict = parse_regions_files("files/area.txt")
	region_dict = parse_regions_files("files/region.txt")
	superregion_dict = parse_regions_files("files/superregion.txt")

	province_stats_list = []
	province_list = split("-\d+=[{]", provinces)[1:]
	for province, x in zip(province_list, range(len(province_list))):
		province_list[x] = province.split("history")[0]
		province_list[x] += province.split("discovered_by=")[-1]

	province_regex = "name=\"(?P<name>[^\n]+)\".+?trade=\"(?P<trade_node>[^\n]+)\".+?" \
					 "base_tax=(?P<base_tax>[^\n]+).+?" \
					 "base_production=(?P<base_production>[^\n]+).+?base_manpower=(?P<base_manpower>[^\n]+).+?" \
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
	# province_hre = compile("hre=(?P<hre>[^\n]+)")
	province_id = 0

	for province in province_list:
		province_id += 1
		try:
			id_index_dict[province_id] = len(province_stats_list)
			result = list(province_x.search(province).groups())
			result.insert(2, result.pop(5))  # Move Trade Goods to Index 2
			for i in range(len(result)):
				if i > 2:
					result[i] = int(result[i].split(".")[0])
			result.append(result[3] + result[4] + result[5])  # Total Development
			result.insert(0, province_id)

			owner = province_x2.search(province)
			if owner:
				result.insert(2, owner.group(1))
			else:
				result.insert(2, "uncolonized")

			religion = province_x3.search(province)
			if religion:
				result.insert(4, religion.group(1))
			else:
				result.insert(4, "no religion")

			culture = province_x4.search(province)
			if culture:
				result.insert(4, culture.group(1))
			else:
				result.insert(4, "no culture")
			trade_power = province_x5.search(province)
			if trade_power:
				result.append(float(trade_power.group(1)))
			else:
				result.append(0.0)
			province_stats_list.append(result)
		except AttributeError:
			pass
		step += 400 / len(province_list)
		pbar.setValue(step)

	for area in area_dict:
		for province_id in area_dict[area]:
			if len(province_stats_list[id_index_dict[province_id]]) == 12:
				province_stats_list[id_index_dict[province_id]].append(area)
		step += 200 / len(area_dict)
		pbar.setValue(step)

	for province in province_stats_list:
		for region in region_dict:
			if province[-1] in region_dict[region]:
				province.append(region)

		for superregion in superregion_dict:
			if province[-1] in superregion_dict[superregion]:
				province.append(superregion)
		step += 400 / len(province_list)
		pbar.setValue(step)
	for a, b in zip(range(len(province_stats_list)), province_stats_list):
		for i in range(5):
			b.insert(3, b.pop(11))  # Moves Tax, Production, Manpower, Development & Trade Power a little bit up front
	return province_stats_list


def parse_wars(content):
	""" Second part of the main parser. Reads all relevant information about wars
	from the savegame. Returns a list of all wars, as well as a dictionary about
	the participants in each war."""
	previous_wars = content.split("previous_war={")[0].split("active_war={")[1:] + content.split("previous_war={")[1:]
	compile_wars = compile("name=\"(?P<name>.+?)\"\n\thistory", DOTALL)
	compile_participants = compile(
		"value=(?P<value>.+?)\n\t\ttag=\"(?P<tag>.+?)\".+?members={\n\t\t\t\t(?P<losses>[^\n]+)", DOTALL)
	war_list = []
	par_list = []
	for war in previous_wars:
		result = compile_wars.search(war)
		if result:
			war_list.append(result.group(1))
		participants = war.split("participants={")[1:]
		if participants:
			pars = []
			for par in participants:
				result = compile_participants.search(par)
				pars.append(list(result.groups()))
				pars[-1][-1] = [int(p) for p in pars[-1][-1].split()]
				pars[-1][0] = float(pars[-1][0])
				pars[-1].append(pars[-1][2][0] + pars[-1][2][1])  # Inf
				pars[-1].append(pars[-1][2][3] + pars[-1][2][4])  # Cav
				pars[-1].append(pars[-1][2][6] + pars[-1][2][7])  # Art
				pars[-1].append(pars[-1][2][0] + pars[-1][2][3] + pars[-1][2][6])  # Combat
				pars[-1].append(pars[-1][2][1] + pars[-1][2][4] + pars[-1][2][7])  # Attrition
				pars[-1].append(
					pars[-1][2][0] + pars[-1][2][3] + pars[-1][2][6] + pars[-1][2][1] + pars[-1][2][4] + pars[-1][2][
						7])  # Total
				del pars[-1][2]
				pars[-1].insert(0, pars[-1].pop(1))

			par_list.append(pars)
		else:
			if result:
				del war_list[-1]
	for war in par_list:
		total_losses = ["Total", 0, 0, 0, 0, 0, 0, 0]
		for country in war:
			for i in range(7):
				total_losses[i + 1] += country[i + 1]
		war.append(total_losses)
	return dict(zip(war_list, par_list)), war_list


def parse_battles(content, war_list, pbar, plabel):
	step = 0
	pbar.reset()
	plabel.setText("Loading Battle Data...")

	war_list = []
	compile_wars = compile("name=\"(?P<name>.+?)\"\n\thistory", DOTALL)

	battles = content.split("\ncombat={")[1]
	battles = battles.split("income_statistics")[0]
	active_wars, *previous_wars = content.split("previous_war={")
	active_wars = active_wars.split("active_war={")[1:]
	total_wars = active_wars + previous_wars

	for war in total_wars:
		battle = war.split("battle={")[1:]
		for b in battle:
			war_list.append(compile_wars.search(war).group(1))

	battle_list = battles.split("battle={")
	first_year = battle_list.pop(0).split("\n")[-2].split("={")[0].split()
	battle_regex = "name=\"(?P<province>[^\n]+)\".+?result=(?P<result>[^\n]+).+?" \
				   "attacker=[{](?P<attacker>[^}]+).+?defender=[{](?P<defender>[^}]+).+?"
	battle_x = compile(battle_regex, DOTALL)

	result_list = []
	for battle, i in zip(battle_list, range(len(battle_list))):
		result = battle_x.findall(battle)
		result = list(result[0])
		last_line = battle.split("\n")[-2].split("={")[0].split()
		commander = result[2].split("commander=")[1].split("\"")[1]
		result[2] = result[2].split("commander=")[0]
		result[2] = result[2].split()
		result[2].append("commander={0}".format(commander))
		commander = result[3].split("commander=")[1].split("\"")[1]
		result[3] = result[3].split("commander=")[0]
		result[3] = result[3].split()
		result[3].append("commander={0}".format(commander))
		result.append(last_line)
		result_list.append(result)
		if i == 0:
			result_list[i].insert(-1, first_year)
		else:
			result_list[i].insert(-1, result_list[i - 1].pop(-1))
		if (i + 1) == len(battle_list):
			del result_list[i][-1]
		step += 1000 / len(battle_list)
		pbar.setValue(step)
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

	return filtered_army_battle_list, filtered_navy_battle_list


def parse_incomestat(content, savegame_list, formable_nations_dict, pbar, plabel,\
					all_nations_bool, stats_dict, playertags):
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
		if (tag in playertags) or all_nations_bool:
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


def parse_trade(content, pbar, plabel):
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


def compile_subjects(info, tag, subject_dict, trade_port_dict, old_version_flag=False):
	compile_subjects = compile("\n\t\tsubjects={([^}]+)}")
	compile_trade_port = compile("trade_port=(.+)")
	result = compile_subjects.search(info)
	if result:
		if old_version_flag:
			subject_dict[tag] = [country.split("\"")[1] for country in result.group(1).split()]
		else:
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
		stats_dict[tag]["points_spent"] = [adm_points_dict, dip_points_dict, mil_points_dict, total_points_dict]
	except:
		if tag in stats_dict.keys():
			stats_dict[tag]["points_spent"] = [adm_points_dict, dip_points_dict, mil_points_dict, total_points_dict]


def parse_countries(content, playertags, all_nations_bool, pbar, plabel):
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


def parse_history(content):
	countries = split("\n\t([A-Z0-9]{3})", content.split("\ncountries={")[1].split('active_advisors')[0])
	tag_list, info_list = countries[1:-1:2], countries[2:-1:2]
	compile_monarch_id = compile("\tmonarch={\n\t\t\tid=(\d+)")
	monarch_dict = {}
	for tag, country in zip(tag_list, info_list):
		result = compile_monarch_id.search(country)
		if result:
			monarch_id = result.group(1)
			compile_monarch_info = compile(
				"id={\n.+id=" + monarch_id + ".+?name=(.+?)\".+?country=\"(.+?)\".+?DIP=(\d).+?ADM=(\d).+?MIL=(\d).+?",
				DOTALL)
			result = compile_monarch_info.search(country.split("original_capital")[0])
			if result:
				monarch_dict[tag] = result.groups()


def parse(filename, playertags, savegame_list, formable_nations_dict, all_nations_bool, pbar, plabel):
	with open(filename, 'r') as sg:
		content = sg.read()
		provinces = content.split("\nprovinces={")[1].split("countries={")[0]

		year = findall("date=(?P<year>\d{4})", content)[0]
		total_trade_goods = list(map(float, list(findall("tradegoods_total_produced={\n(.+)", content)[0].split())))
		compile_hre_reformlevel = compile("reform_level=(\d)")
		try:
			hre_reformlevel = int(compile_hre_reformlevel.search(content).group(1))
		except:
			hre_reformlevel = 0
		province_stats_list = parse_provinces(provinces, pbar, plabel)
		war_dict, war_list = parse_wars(content)
		army_battle_list, navy_battle_list = parse_battles(content, war_list, pbar, plabel)
		stats_dict, sorted_tag_list, subject_dict, color_dict, \
		trade_port_dict, tech_dict = parse_countries(content, playertags, all_nations_bool, pbar, plabel)
		income_dict = parse_incomestat(content, savegame_list, formable_nations_dict, pbar, plabel,
									   all_nations_bool, stats_dict, playertags)
		trade_stats_list = parse_trade(content, pbar, plabel)
		parse_history(content)
	pbar.reset()
	plabel.clear()
	return stats_dict, year, total_trade_goods, sorted_tag_list, income_dict, color_dict, army_battle_list, navy_battle_list, province_stats_list, trade_stats_list, subject_dict, hre_reformlevel, trade_port_dict, war_list, war_dict, tech_dict
