import re

filename = "paradox_files/1.30/tags.txt"
filename2 = "paradox_files/1.30/extra_tags.txt"
filename3 = "paradox_files/1.30/extra_extra_tags.txt"
savefile = "parsed_paradox_files/tags.txt"

encoding = "utf-8"

with open(filename, "r", encoding=encoding) as sg:
    content = sg.read()
    regex = re.compile("\n.([A-Z]{3}):\d.\"(.+?)\"")
    results = regex.findall(content)
    tag_dict = {}
    for tag,name in results:
        tag_dict[tag] = name

with open(filename2, "r", encoding=encoding) as sg:
    content = sg.read()
    results = regex.findall(content)
    for tag,name in results:
        tag_dict[tag] = name

with open(filename3, "r", encoding=encoding) as sg:
    content = sg.read()
    results = regex.findall(content)
    for tag,name in results:
        tag_dict[tag] = name

with open(savefile, "w", encoding=encoding) as sg:
	sg.write(str(tag_dict))
