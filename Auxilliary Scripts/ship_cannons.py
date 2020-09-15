import os
from re import compile

ship_type = compile('base_cannons = (\d+)')
unit_type_dict = {}

dir = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Europa Universalis IV\\common\\units"
for file in os.listdir(dir):
    filename = os.fsdecode(file)
    if not filename.endswith(".py"):
        with open(dir + "\\" + filename, 'r') as file:
            content = file.read()
            result = ship_type.search(content)
            if result:
                unit_type_dict[filename.split(".")[0]] = int(result.group(1))


with open("C:\\Users\\kunde\\Documents\\GitHub\\EU4-MP-Statstool\\Statstool-Web\\files\\ship_cannons.txt", "w") as file:
    file.write(str(unit_type_dict))
