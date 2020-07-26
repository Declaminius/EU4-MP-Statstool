from statstool_web import db
from statstool_web.models import Nation, TradeGood, Province, Area, Region, SuperRegion

trade_goods_list = ['', 'Getreide', 'Wein', 'Wolle', 'Tuch', 'Fisch', 'Pelze', 'Salz',
					'Schiffsbedarf', 'Kupfer', 'Gold', 'Eisen', 'Sklaven', 'Elfenbein',
					'Tee', 'Porzellan', 'Gewürze', 'Kaffee', 'Baumwolle', 'Zucker', 'Tabak',
					'Kakao', 'Seide', 'Farbstoffe', 'Tropenholz', 'Vieh', 'Weihrauch', 'Glas',
					'Papier', 'Edelsteine', '', 'Unbekannt']

db.drop_all()
db.create_all()
for name in trade_goods_list:
    trade_good = TradeGood(name = name)
    db.session.add(trade_good)

with open("files/tags.txt", "r", encoding = 'utf-8') as tags:
    localisation_dict = eval(tags.read())
    for key,value in localisation_dict.items():
        nation = Nation(tag = key, name = value)
        db.session.add(nation)

with open("files/superregion.txt", "r", encoding = 'cp1252') as sg:
	superregion_dict = eval(sg.read())
	for key,value in superregion_dict.items():
		superregion = SuperRegion(name = key)
		db.session.add(superregion)
		for name in value:
			region = Region(name = name, superregion = superregion)
			db.session.add(region)

with open("files/region.txt", "r", encoding = 'cp1252') as sg:
	region_dict = eval(sg.read())
	for key,value in region_dict.items():
		region = Region.query.filter_by(name = key).first()
		for name in value:
			area = Area(name = name, region = region)
			db.session.add(area)

with open("files/area.txt", "r", encoding = 'cp1252') as sg:
	area_dict = eval(sg.read())
	with open("files/provinces.txt", "r", encoding = 'cp1252') as sg2:
		province_dict = eval(sg2.read())
		for key,value in area_dict.items():
			area = Area.query.filter_by(name = key).first()
			for id in value:
				province = Province(id = id, name = province_dict[id], area = area)
				db.session.add(province)


db.session.commit()
#Todo: create tags, trade_goods, ... (all static values)