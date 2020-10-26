from statstool_web import create_app, db, bcrypt
from statstool_web.models import Nation, TradeGood, Province, Area, Region, SuperRegion, MP, User
import re

with open("../paradox_files/1.30/00_tradegoods.txt", "r") as file:
	content = file.read()
	trade_goods = re.findall("\n(\w+) = {", content)

app = create_app()
app.app_context().push()

db.drop_all()
db.create_all()

empty_trade_good = TradeGood(name = "")
db.session.add(empty_trade_good)
for name in trade_goods:
    trade_good = TradeGood(name = name)
    db.session.add(trade_good)

with open("../parsed_paradox_files/tags.txt", "r", encoding = 'utf-8') as tags:
    localisation_dict = eval(tags.read())
    for key,value in localisation_dict.items():
        nation = Nation(tag = key, name = value)
        db.session.add(nation)

with open("../parsed_paradox_files/superregion.txt", "r", encoding = 'cp1252') as sg:
	superregion_dict = eval(sg.read())
	for key,value in superregion_dict.items():
		superregion = SuperRegion(name = key)
		db.session.add(superregion)
		for name in value:
			region = Region(name = name, superregion = superregion)
			db.session.add(region)

with open("../parsed_paradox_files/region.txt", "r", encoding = 'cp1252') as sg:
	region_dict = eval(sg.read())
	for key,value in region_dict.items():
		region = Region.query.filter_by(name = key).first()
		for name in value:
			area = Area(name = name, region = region)
			db.session.add(area)

with open("../parsed_paradox_files/area.txt", "r", encoding = 'cp1252') as sg:
	area_dict = eval(sg.read())
	with open("../parsed_paradox_files/provinces.txt", "r", encoding = 'cp1252') as sg2:
		province_dict = eval(sg2.read())
		for key,value in area_dict.items():
			area = Area.query.filter_by(name = key).first()
			for id in value:
				province = Province(id = id, name = province_dict[id], area = area)
				db.session.add(province)

hashed_password = bcrypt.generate_password_hash(app.config["ADMIN_PASSWORD"]).decode('utf-8')
admin = User(id = 1, username = app.config["ADMIN_NAME"], email = app.config["ADMIN_EMAIL"], password = hashed_password)
so_mp = MP(id = 1, name = app.config["MP_NAME"], admin = admin)
db.session.add(so_mp)
db.session.add(admin)
db.session.commit()
#Todo: create tags, trade_goods, ... (all static values)
