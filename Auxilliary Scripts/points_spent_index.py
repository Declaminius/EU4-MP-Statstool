from re import split, findall

with open("savegames/#DanzigKrieg/mp_Mewar1735_05_01.eu4", 'r') as sg:
	content = sg.read()
	countries = split("adm_spent_indexed={", content.split("\ncountries={")[1].split('active_advisors')[0])
	points_spent_list = [i.split("innovativeness")[0] for i in countries[1:]]
	tag_list = [findall("\n\t([A-Z0-9]{3})", i)[-1] for i in countries [:-1]]
	country_list = []
	for i in points_spent_list:
		adm_merge_dict, dip_merge_dict, mil_merge_dict = {}, {}, {}
		try:
			adm, dip, mil = i.split("indexed")
		except:
			pass
		for cat, dic in zip([adm, dip, mil],[adm_merge_dict, dip_merge_dict, mil_merge_dict]):
			cat = findall("\d+=\d+", cat)
			for c in cat:
				key, number = c.split("=")
				dic[int(key)] = int(number)
		country_list.append([adm_merge_dict, dip_merge_dict, mil_merge_dict])
	print(country_list)
