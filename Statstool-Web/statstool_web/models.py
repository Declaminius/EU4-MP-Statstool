from statstool_web import db
import enum
from colour import Color
from sqlalchemy_utils import ColorType

class PointCategories(enum.Enum):
    adm = "adm"
    dip = "dip"
    mil = "mil"
    total = "total"

class PlotTypes(enum.Enum):
    income = "income"
    max_manpower = "max_manpower"
    income_over_time_total = "income_over_time_total"
    income_over_time_latest = "income_over_time_latest"
    infantry = "infantry"
    cavalry = "cavalry"
    artillery = "artillery"
    combat = "combat"
    attrition = "attrition"
    total = "total"
    development = "development"
    effective_development = "effective_development"

savegame_nations = db.Table('savegame_nations',
    db.Column('savegame_id', db.Integer, db.ForeignKey('savegame.id')),
    db.Column('nation_tag', db.String(3), db.ForeignKey('nation.tag'))
)

savegame_player_nations = db.Table('savegame_player_nations',
    db.Column('savegame_id', db.Integer, db.ForeignKey('savegame.id')),
    db.Column('nation_tag', db.String(3), db.ForeignKey('nation.tag'))
)

war_attacker = db.Table('war_attacker',
    db.Column('war_id', db.Integer, db.ForeignKey('war.id')),
    db.Column('attacker_tag', db.String(3), db.ForeignKey('nation.tag'))
)

war_defender = db.Table('war_defender',
    db.Column('war_id', db.Integer, db.ForeignKey('war.id')),
    db.Column('defender_tag', db.String(3), db.ForeignKey('nation.tag'))
)

class MP(db.Model):
    __tablename__ = 'mp'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    savegames = db.relationship("Savegame", backref = "mp", lazy = True)

class Savegame(db.Model):
    __tablename__ = 'savegame'
    id = db.Column(db.Integer, primary_key = True)
    mp_id = db.Column(db.Integer, db.ForeignKey('mp.id'))
    year = db.Column(db.Integer, default = None)
    file = db.Column(db.String(120), nullable = False)
    map_file = db.Column(db.String(120), nullable = True)
    parse_flag = db.Column(db.Boolean, default = False, nullable = False)
    nations = db.relationship("Nation", secondary = savegame_nations)
    player_nations = db.relationship("Nation", secondary = savegame_player_nations)
    army_battles = db.relationship("ArmyBattle", backref = "savegame")
    navy_battles = db.relationship("NavyBattle", backref = "savegame")
    wars = db.relationship("War", backref = "savegame")

class NationFormation(db.Model):
    __tablename__ = 'nation_formation'
    old_savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)
    new_savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)
    old_nation_tag = db.Column(db.String(3), db.ForeignKey('nation.tag'), primary_key = True)
    new_nation_tag = db.Column(db.String(3), db.ForeignKey('nation.tag'), primary_key = True)

class SavegamePlots(db.Model):
    __tablename__ = 'savegame_plots'
    filename = db.Column(db.String, primary_key = True)
    type = db.Column(db.Enum(PlotTypes), nullable = False)
    old_savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'))
    new_savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'))

class Nation(db.Model):
    __tablename__ = 'nation'
    tag = db.Column(db.String(3), primary_key = True)
    name = db.Column(db.String)

class NationSavegameData(db.Model):
    __tablename__ = "nation_savegame_data"
    nation_tag = db.Column(db.String(3), db.ForeignKey('nation.tag'), primary_key = True)
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)

    effective_development = db.Column(db.Float, default = 0)
    development = db.Column(db.Integer, default = 0)
    great_power_score = db.Column(db.Integer, default = 0)
    navy_strength = db.Column(db.Float, default = 0)
    income = db.Column(db.Float, default = 0)
    manpower = db.Column(db.Integer, default = 0)
    max_manpower = db.Column(db.Integer, default = 0)
    adm_tech = db.Column(db.Integer, default = 3)
    dip_tech = db.Column(db.Integer, default = 3)
    mil_tech = db.Column(db.Integer, default = 3)
    number_of_ideas = db.Column(db.Integer, default = 0)
    institution_penalty = db.Column(db.Float, default = 1)
    innovativeness = db.Column(db.Float, default = 0)
    color = db.Column(ColorType, default = Color('#ffffff'))

    #Siegpunkte
    highest_ae = db.Column(db.Float, default = 0)
    num_of_colonies = db.Column(db.Integer, default = 0)
    num_converted_religion = db.Column(db.Integer, default = 0)
    total_buildings_value = db.Column(db.Integer, default = 0)
    standing_army = db.Column(db.Float, default = 0)
    navy_cannons = db.Column(db.Integer, default = 0)


    savegame = db.relationship("Savegame", backref="nation_data")
    nation = db.relationship("Nation", backref="savegame_data")

class NationSavegameGoodsProduced(db.Model):
    __tablename__ = "nation_savegame_goods_produced"
    nation_tag = db.Column(db.String(3), db.ForeignKey('nation.tag'), primary_key = True)
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)
    trade_good_id = db.Column(db.Integer, db.ForeignKey('trade_good.id'), primary_key = True)
    amount = db.Column(db.Float, default = 0)

    savegame = db.relationship("Savegame", backref="nation_goods_produced")
    nation = db.relationship("Nation", backref="savegame_goods_produced")

class NationSavegamePointsSpent(db.Model):
    __tablename__ = 'nation_savegame_points_spent'
    nation_tag = db.Column(db.String(3), db.ForeignKey('nation.tag'), primary_key = True)
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)
    points_spent_id = db.Column(db.Integer, db.ForeignKey('points_spent.id'), primary_key = True)
    points_spent_category = db.Column(db.Enum(PointCategories), db.ForeignKey('points_spent.category'), primary_key = True)
    amount = db.Column(db.Integer, default = 0)

    savegame = db.relationship("Savegame", backref="nation_points_spent")
    nation = db.relationship("Nation", backref="savegame_points_spent")

class NationSavegameIncomePerYear(db.Model):
    __tablename__ = 'nation_savegame_income_per_year'
    nation_tag = db.Column(db.String(3), db.ForeignKey('nation.tag'), primary_key = True)
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)
    year = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.Integer, default = 0)

    savegame = db.relationship("Savegame", backref="nation_income_year")
    nation = db.relationship("Nation", backref="savegame_income_year")

class NationSavegameArmyLosses(db.Model):
    __tablename__ = 'nation_savegame_army_losses'
    nation_tag = db.Column(db.String(3), db.ForeignKey('nation.tag'), primary_key = True)
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)

    infantry = db.Column(db.Integer, default = 0)
    cavalry = db.Column(db.Integer, default = 0)
    artillery = db.Column(db.Integer, default = 0)
    attrition = db.Column(db.Integer, default = 0)
    combat = db.Column(db.Integer, default = 0)
    total = db.Column(db.Integer, default = 0)

    color = db.Column(ColorType, default = Color('#ffffff'))

    savegame = db.relationship("Savegame", backref="nation_army_losses")
    nation = db.relationship("Nation", backref="savegame_army_losses")

class NationSavegameNavyLosses(db.Model):
    __tablename__ = 'nation_savegame_navy_losses'
    nation_tag = db.Column(db.String(3), db.ForeignKey('nation.tag'), primary_key = True)
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)

    heavy_ships = db.Column(db.Integer, default = 0)
    light_ships = db.Column(db.Integer, default = 0)
    galleys = db.Column(db.Integer, default = 0)
    transports = db.Column(db.Integer, default = 0)
    attrition = db.Column(db.Integer, default = 0)
    combat = db.Column(db.Integer, default = 0)
    total = db.Column(db.Integer, default = 0)

    savegame = db.relationship("Savegame", backref="nation_navy_losses")
    nation = db.relationship("Nation", backref="savegame_navy_losses")

class SavegameProvinces(db.Model):
    __tablename__ = 'savegame_provinces'
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)
    province_id = db.Column(db.Integer, db.ForeignKey('province.id'), primary_key = True)

    nation_tag = db.Column(db.String(3), db.ForeignKey('nation.tag'), nullable = True)
    trade_good_id = db.Column(db.Integer, db.ForeignKey('trade_good.id'))

    base_tax = db.Column(db.Integer)
    base_production = db.Column(db.Integer)
    base_manpower = db.Column(db.Integer)
    development = db.Column(db.Integer)

    religion = db.Column(db.String, nullable = True)
    culture = db.Column(db.String, nullable = True)

    trade_power = db.Column(db.Float, default = 0.0)

    savegame = db.relationship("Savegame", backref="nation_provinces")

class PointsSpent(db.Model):
    __tablename__ = 'points_spent'
    id = db.Column(db.Integer, primary_key = True)
    category = db.Column(db.Enum(PointCategories), primary_key = True)
    name = db.Column(db.Integer, default = '?')

class TradeGood(db.Model):
    __tablename__ = 'trade_good'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)

class TotalGoodsProduced(db.Model):
    __tablename__ = "total_goods_produced"
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)
    trade_good_id = db.Column(db.Integer, db.ForeignKey('trade_good.id'), primary_key = True)
    amount = db.Column(db.Float, default = 0)
    savegame = db.relationship("Savegame", backref="total_trade_goods")
    trade_good = db.relationship("TradeGood", backref="total_trade_goods")

class ArmyBattle(db.Model):
    __tablename__ = 'army_battle'
    id = db.Column(db.Integer, primary_key = True)
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'))
    war_id = db.Column(db.Integer, db.ForeignKey('war.id'))
    date = db.Column(db.Date, nullable = False)
    result = db.Column(db.String)

    attacker_country = db.Column(db.String, db.ForeignKey('nation.tag'))
    attacker_infantry = db.Column(db.Integer, default = 0)
    attacker_cavalry = db.Column(db.Integer, default = 0)
    attacker_artillery = db.Column(db.Integer, default = 0)
    attacker_total = db.Column(db.Integer, default = 0)
    attacker_losses = db.Column(db.Integer, default = 0)
    attacker_commander = db.Column(db.String, default = "")

    defender_country = db.Column(db.String, db.ForeignKey('nation.tag'))
    defender_infantry = db.Column(db.Integer, default = 0)
    defender_cavalry = db.Column(db.Integer, default = 0)
    defender_artillery = db.Column(db.Integer, default = 0)
    defender_total = db.Column(db.Integer, default = 0)
    defender_losses = db.Column(db.Integer, default = 0)
    defender_commander = db.Column(db.String, default = "")

    total_combatants = db.Column(db.Integer, default = 0)
    total_losses = db.Column(db.Integer, default = 0)

    province = db.Column(db.String)

class NavyBattle(db.Model):
    __tablename__ = 'navy_battle'
    id = db.Column(db.Integer, primary_key = True)
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'))
    war_id = db.Column(db.Integer, db.ForeignKey('war.id'))
    date = db.Column(db.Date, nullable = False)
    result = db.Column(db.String)

    attacker_country = db.Column(db.String, db.ForeignKey('nation.tag'))
    attacker_heavy_ship = db.Column(db.Integer)
    attacker_light_ship = db.Column(db.Integer)
    attacker_galley = db.Column(db.Integer)
    attacker_transport = db.Column(db.Integer)
    attacker_losses = db.Column(db.Integer)
    attacker_commander = db.Column(db.String, default = "")

    defender_country = db.Column(db.String, db.ForeignKey('nation.tag'))
    defender_heavy_ship = db.Column(db.Integer)
    defender_light_ship = db.Column(db.Integer)
    defender_galley = db.Column(db.Integer)
    defender_transport = db.Column(db.Integer)
    defender_losses = db.Column(db.Integer)
    defender_commander = db.Column(db.String, default = "")

    province = db.Column(db.String)

class Province(db.Model):
    __tablename__ = "province"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"))

class Area(db.Model):
    __tablename__ = "area"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    region_id = db.Column(db.Integer, db.ForeignKey("region.id"))
    provinces = db.relationship("Province", backref = "area")

class Region(db.Model):
    __tablename__ = "region"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    superregion_id = db.Column(db.Integer, db.ForeignKey("superregion.id"))
    areas = db.relationship("Area", backref = "region")

class SuperRegion(db.Model):
    __tablename__ = "superregion"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    provinces = db.relationship("Region", backref = "superregion")

class War(db.Model):
    __tablename__ = "war"
    id = db.Column(db.Integer, primary_key = True)
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'))
    name = db.Column(db.String, default = False)
    ongoing = db.Column(db.Boolean)

    infantry = db.Column(db.Integer, default = 0)
    cavalry = db.Column(db.Integer, default = 0)
    artillery = db.Column(db.Integer, default = 0)
    attrition = db.Column(db.Integer, default = 0)
    combat = db.Column(db.Integer, default = 0)
    total = db.Column(db.Integer, default = 0)

    participants = db.relationship("WarParticipant")
    army_battles = db.relationship("ArmyBattle")
    navy_battles = db.relationship("NavyBattle")

class WarParticipant(db.Model):
    __tablename__ = "war_participant"
    war_id = db.Column(db.Integer, db.ForeignKey("war.id"), primary_key = True)
    nation_tag = db.Column(db.String(3), db.ForeignKey('nation.tag'), primary_key = True)

    participation_score = db.Column(db.Float)
    infantry = db.Column(db.Integer)
    cavalry = db.Column(db.Integer)
    artillery = db.Column(db.Integer)
    attrition = db.Column(db.Integer)
    combat = db.Column(db.Integer)
    total = db.Column(db.Integer)

class Monarch(db.Model):
    __tablename__ = "monarch"
    id = db.Column(db.Integer, primary_key = True)
    nation_tag = db.Column(db.String(3), db.ForeignKey("nation.tag"))
    savegame_id = db.Column(db.Integer, db.ForeignKey("savegame.id"))

    name = db.Column(db.String)
    adm = db.Column(db.Integer)
    dip = db.Column(db.Integer)
    mil = db.Column(db.Integer)

    #TODO
