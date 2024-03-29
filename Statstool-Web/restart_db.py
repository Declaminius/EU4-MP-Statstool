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
so_mp1 = MP(id = 1, name = "Sonntags-MP: S2E2 - Per Aspera Ad Astra",
			description = "Statistiken und Siegpunkts-Übersicht für das 17.Sonntags-MP der Strategie-Zone.",
			gm = "Declaminius", host = "Wassergeist", admin = admin)
so_mp2 = MP(id = 2, name = "Sonntags-MP: S2E3 - Faber est suae quisque fortunae",
			description = "Statistiken und Siegpunkts-Übersicht für das 18.Sonntags-MP der Strategie-Zone." ,
			gm = "Declaminius", host = "RoLJZ1", checksum = "f22f", next_gameday = "14.02.2021", admin = admin)
so_mp3 = MP(id = 3, name = "Sonntags-MP: S2E4 - Noch zwei Desynchs bis 1821!",
			description = "Statistiken und Siegpunkts-Übersicht für das 19.Sonntags-MP der Strategie-Zone." ,
			gm = "Declaminius", host = "Sam", checksum = "????", next_gameday = "09.05.2021", admin = admin)
db.session.add(so_mp1)
db.session.add(so_mp2)
db.session.add(so_mp3)
db.session.add(admin)
db.session.commit()
#Todo: create tags, trade_goods, ... (all static values)
