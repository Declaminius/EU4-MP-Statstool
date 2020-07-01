import re

filename = "paradox_files/1.30/tags.txt"
filename2 = "paradox_files/1.30/extra_tags.txt"
savefile = "files/tags.txt"


with open(filename, "r") as sg:
    content = sg.read()
    regex = re.compile("\n.([A-Z]{3}):\d.\"(.+?)\"")
    results = regex.findall(content)
    tag_dict = {}
    for tag,name in results:
        tag_dict[tag] = name

with open(filename2, "r", encoding="utf8") as sg:
    content = sg.read()
    results = regex.findall(content)
    for tag,name in results:
        tag_dict[tag] = name

with open(savefile, "w") as sg:
	sg.write(str(tag_dict))
