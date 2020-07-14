import re

filename = "paradox_files/1.30/positions.txt"

savefile = "files/provinces.txt"

encoding = "cp1252"

with open(filename, "r", encoding=encoding) as sg:
    content = sg.read()
    results = re.findall("#(.+)\n(\d+?)=", content)
    province_id_dict = {}
    for name,id in results:
        province_id_dict[int(id)] = name

with open(savefile, "w", encoding=encoding) as sg:
	sg.write(str(province_id_dict))
