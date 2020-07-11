from statstool_web import db
from statstool_web.models import *

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

db.session.commit()
#Todo: create tags, trade_goods, provinces, ... (all static values)
