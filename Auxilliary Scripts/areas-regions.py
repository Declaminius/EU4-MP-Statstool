import re

filename = "paradox_files/1.30/area.txt"
filename2 = "paradox_files/1.30/region.txt"
filename3 = "paradox_files/1.30/superregion.txt"
savefile = "files/area.txt"
savefile2 = "files/region.txt"
savefile3 = "files/superregion.txt"

with open(filename, "r") as sg:
	content = sg.read()
	land_area = content.split("#Deprecated:")[0].split("Land Areas")[1]
	regex = "\w+.*?=.*?{.*?\n([^}]+)\n"
	area_regex = "\w+_\w+"
	color = re.finditer("\n\tcolor = {.+}", land_area)
	new_land_area = ""
	start = 0
	for result in color:
		new_land_area += land_area[start:result.start()]
		start = result.end()
	new_land_area += land_area[start:]
	comp = re.compile(regex, re.DOTALL)
	comp2 = re.compile(area_regex, re.DOTALL)
	a_list = comp2.findall(new_land_area)
	b_results = comp.findall(new_land_area)
	b_list = []
	for b in b_results:
		b_list.append([int(c) for c in b.split()])


with open(savefile, "w") as sg:
	sg.write(str(dict(zip(a_list, b_list))))


with open (filename2, "r") as sg:
	content = sg.read()
	content = content.split("EUROPE")[1].split("Sea Regions")[0]
	regex = "\n(\w+) =.*?{.+?areas = {([^}]+)"
	comp = re.compile(regex, re.DOTALL)
	c_tuple = comp.findall(content)
	c_list = []
	d_list = []
	for c in c_tuple:
		c0 = c[0]
		c1 = c[1].split()
		c_list.append(c0)
		d_list.append(c1)

with open(savefile2, "w") as sg:
	sg.write(str(dict(zip(c_list, d_list))))

with open (filename3, "r") as sg:
	content = sg.read()
	content = content.split("new_world_superregion")[0]
	regex = "(\w+) =.*?{([^}]+)"
	comp = re.compile(regex, re.DOTALL)
	d_tuple = comp.findall(content)
	e_list = []
	f_list = []
	for d in d_tuple:
		d0 = d[0]
		d1 = d[1].split()
		e_list.append(d0)
		f_list.append(d1)

with open(savefile3, "w") as sg:
	sg.write(str(dict(zip(e_list, f_list))))
