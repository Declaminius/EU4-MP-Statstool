from statstool_web import db
import enum
from colour import Color
from sqlalchemy_utils import ColorType

class PointCategories(enum.Enum):
    adm = "adm"
    dip = "dip"
    mil = "mil"
    total = "total"

savegame_nations = db.Table('savegame_nations',
    db.Column('savegame_id', db.Integer, db.ForeignKey('savegame.id')),
    db.Column('nation_tag', db.String(3), db.ForeignKey('nation.tag'))
)

savegame_player_nations = db.Table('savegame_player_nations',
    db.Column('savegame_id', db.Integer, db.ForeignKey('savegame.id')),
    db.Column('nation_tag', db.String(3), db.ForeignKey('nation.tag'))
)

savegame_army_battles = db.Table('savegame_army_battles',
    db.Column('savegame_id', db.Integer, db.ForeignKey('savegame.id')),
    db.Column('battle_id', db.Integer, db.ForeignKey('army_battle.id'))
)

savegame_wars = db.Table('savegame_wars',
    db.Column('savegame_id', db.Integer, db.ForeignKey('savegame.id')),
    db.Column('war_id', db.Integer, db.ForeignKey('war.id'))
)

nation_data = db.Table('nation_data',
    db.Column('nation_tag', db.String(3), db.ForeignKey('nation.tag')),
    db.Column('data_id', db.Integer, db.ForeignKey('data.id'))
)

nation_tech = db.Table('nation_tech',
    db.Column('nation_tag', db.String(3), db.ForeignKey('nation.tag')),
    db.Column('tech_id', db.Integer, db.ForeignKey('tech.id'))
)

# nation_subjects = db.Table('nation_subjects',
#     db.Column('overlord_tag', db.String(3), db.ForeignKey('nation.tag')),
#     db.Column('subject_tag', db.String(3), db.ForeignKey('nation.tag'))
# )

data_army_losses = db.Table('data_army_losses',
    db.Column('data_id', db.Integer, db.ForeignKey('data.id')),
    db.Column('army_losses_id', db.Integer, db.ForeignKey('army_losses.id'))
)

data_navy_losses = db.Table('data_navy_losses',
    db.Column('data_id', db.Integer, db.ForeignKey('data.id')),
    db.Column('navy_losses_id', db.Integer, db.ForeignKey('navy_losses.id'))
)

data_goods_produced = db.Table('data_goods_produced',
    db.Column('data_id', db.Integer, db.ForeignKey('data.id')),
    db.Column('trade_good_id', db.Integer, db.ForeignKey('trade_good.id')),
    db.Column('amount', db.Float, default = 0)
)

data_points_spent = db.Table('data_points_spent',
    db.Column('data_id', db.Integer, db.ForeignKey('data.id')),
    db.Column('point_id', db.Integer),
    db.Column('point_category', db.Enum(PointCategories)),
    db.Column('amount', db.Float, default = 0),
    db.ForeignKeyConstraint(
        ('point_id', 'point_category'),
        ('points_spent.id', 'points_spent.category')
    )
)

data_income_per_year = db.Table('data_income_per_year',
    db.Column('data_id', db.Integer, db.ForeignKey('data.id')),
    db.Column('year', db.Integer, db.ForeignKey('year.year')),
    db.Column('amount', db.Float, default = 0)
)

army_battle_province = db.Table('army_battle_province',
    db.Column('battle_id', db.Integer, db.ForeignKey('army_battle.id')),
    db.Column('province_id', db.Integer, db.ForeignKey('province.id'))
)

navy_battle_province = db.Table('navy_battle_province',
    db.Column('battle_id', db.Integer, db.ForeignKey('navy_battle.id')),
    db.Column('province_id', db.Integer, db.ForeignKey('province.id'))
)

province_stats = db.Table('province_stats',
    db.Column('province_id', db.Integer, db.ForeignKey('province.id')),
    db.Column('province_data_id', db.Integer, db.ForeignKey('province_data.id'))
)

war_attacker = db.Table('war_attacker',
    db.Column('war_id', db.Integer, db.ForeignKey('war.id')),
    db.Column('attacker_tag', db.String(3), db.ForeignKey('nation.tag'))
)

war_defender = db.Table('war_defender',
    db.Column('war_id', db.Integer, db.ForeignKey('war.id')),
    db.Column('defender_tag', db.String(3), db.ForeignKey('nation.tag'))
)

class Savegame(db.Model):
    __tablename__ = 'savegame'
    id = db.Column(db.Integer, primary_key = True)
    year = db.Column(db.Integer, default = None)
    file = db.Column(db.String(120), nullable = False)
    nations = db.relationship("Nation", secondary = savegame_nations)
    player_nations = db.relationship("Nation", secondary = savegame_player_nations)
    total_goods_produced = db.relationship("TradeGood", secondary = savegame_goods_produced)
    army_battles = db.relationship("ArmyBattle", secondary = savegame_army_battles)
    wars = db.relationship("War", secondary = savegame_wars)

class Nation(db.Model):
    __tablename__ = 'nation'
    tag = db.Column(db.String(3), primary_key = True)
    name = db.Column(db.String)
    color = db.Column(ColorType, default = Color('#fefefe'))
    data = db.relationship("Data", secondary = nation_data)
    tech = db.relationship("Tech", secondary = nation_tech)
    #subjects = db.relationship("Nation", secondary = nation_subjects)

class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key = True)
    effective_development = db.Column(db.Float, default = 0)
    development = db.Column(db.Integer, default = 0)
    great_power_score = db.Column(db.Integer, default = 0)
    navy_strength = db.Column(db.Float, default = 0)
    income = db.Column(db.Float, default = 0)
    manpower = db.Column(db.Integer, default = 0)
    max_manpower = db.Column(db.Integer, default = 0)
    total_income = db.Column(db.Integer, default = 0)
    army_losses = db.relationship("ArmyLosses", secondary = data_army_losses)
    navy_losses = db.relationship("NavyLosses", secondary = data_navy_losses)
    goods_produced = db.relationship("TradeGood", secondary = data_goods_produced)
    points_spent = db.relationship("PointsSpent", secondary = data_points_spent)
    income_per_year = db.relationship("Year", secondary = data_income_per_year)

class ArmyLosses(db.Model):
    __tablename__ = 'army_losses'
    id = db.Column(db.Integer, primary_key = True)
    infantry = db.Column(db.Integer, default = 0)
    cavalry = db.Column(db.Integer, default = 0)
    artillery = db.Column(db.Integer, default = 0)
    attrition = db.Column(db.Integer, default = 0)
    combat = db.Column(db.Integer, default = 0)
    total = db.Column(db.Integer, default = 0)


class NavyLosses(db.Model):
    __tablename__ = 'navy_losses'
    id = db.Column(db.Integer, primary_key = True)
    heavy_ships = db.Column(db.Integer, default = 0)
    light_ships = db.Column(db.Integer, default = 0)
    galleys = db.Column(db.Integer, default = 0)
    transports = db.Column(db.Integer, default = 0)
    attrition = db.Column(db.Integer, default = 0)
    combat = db.Column(db.Integer, default = 0)
    total = db.Column(db.Integer, default = 0)

class TradeGood(db.Model):
    __tablename__ = 'trade_good'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)

class TotalGoodsProduced(db.Model):
    __tablename__ = "total_goods_produced"
    savegame_id = db.Column(db.Integer, db.ForeignKey('savegame.id'), primary_key = True)
    trade_good_id = db.Column(db.Integer, db.ForeignKey('trade_good.id'), primary_key = True)
    amount = db.Column(db.Float, default = 0)
    savegame = db.relationship(Community, backref="total_trade_goods")
    trade_good = db.relationship(User, backref="total_trade_goods")


class PointsSpent(db.Model):
    __tablename__ = 'points_spent'
    id = db.Column(db.Integer, primary_key = True)
    category = db.Column(db.Enum(PointCategories), primary_key = True)
    name = db.Column(db.Integer, default = '?')

class Year(db.Model):
    __tablename__ = 'year'
    year = db.Column(db.Integer, primary_key = True)

class ArmyBattle(db.Model):
    __tablename__ = 'army_battle'
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable = False)

    attacker = db.Column(db.String, nullable = False)
    attacker_inf = db.Column(db.Integer)
    attacker_cav = db.Column(db.Integer)
    attacker_art = db.Column(db.Integer)
    attacker_total = db.Column(db.Integer)
    attacker_losses = db.Column(db.Integer)
    attacker_leader = db.Column(db.String, default = "")

    defender = db.Column(db.String, nullable = False)
    defender_inf = db.Column(db.Integer)
    defender_cav = db.Column(db.Integer)
    defender_art = db.Column(db.Integer)
    defender_total = db.Column(db.Integer)
    defender_losses = db.Column(db.Integer)
    defender_leader = db.Column(db.String, default = "")

    war = db.Column(db.String, nullable = False)
    total_units = db.Column(db.Integer)
    total_losses = db.Column(db.Integer)

    province = db.relationship("Province", secondary = army_battle_province)

class NavyBattle(db.Model):
    __tablename__ = 'navy_battle'
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable = False)

    attacker = db.Column(db.String, nullable = False)
    attacker_heavy = db.Column(db.Integer)
    attacker_light = db.Column(db.Integer)
    attacker_galley = db.Column(db.Integer)
    attacker_transport = db.Column(db.Integer)
    attacker_losses = db.Column(db.Integer)
    attacker_leader = db.Column(db.String, default = "")

    defender = db.Column(db.String, nullable = False)
    defender_heavy = db.Column(db.Integer)
    defender_light = db.Column(db.Integer)
    defender_galley = db.Column(db.Integer)
    defender_transport = db.Column(db.Integer)
    defender_losses = db.Column(db.Integer)
    defender_leader = db.Column(db.String, default = "")

    war = db.Column(db.String, nullable = False)
    total_units = db.Column(db.Integer)
    total_losses = db.Column(db.Integer)

    province = db.relationship("Province", secondary = navy_battle_province)

class Province(db.Model):
    __tablename__ = "province"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    data = db.relationship("ProvinceData", secondary = province_stats)

class ProvinceData(db.Model):
    __tablename__ = "province_data"
    id = db.Column(db.Integer, primary_key = True)
    base_tax = db.Column(db.Integer)
    base_production = db.Column(db.Integer)
    base_manpower = db.Column(db.Integer)
    development = db.Column(db.Integer)
    trade_power = db.Column(db.Float)


    #owner = db.relationship("Nation", secondary = province_owner)

class War(db.Model):
    __tablename__ = "war"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    infantry = db.Column(db.Integer)
    cavalry = db.Column(db.Integer)
    artillery = db.Column(db.Integer)
    attrition = db.Column(db.Integer)
    combat = db.Column(db.Integer)
    total = db.Column(db.Integer)

    attacker = db.relationship("Nation", secondary = war_attacker)
    defender = db.relationship("Nation", secondary = war_defender)

class Tech(db.Model):
    __tablename__ = "tech"
    id = db.Column(db.Integer, primary_key = True)
    adm_tech = db.Column(db.Integer)
    dip_tech = db.Column(db.Integer)
    mil_tech = db.Column(db.Integer)
    number_of_ideas = db.Column(db.Integer)
    institution_penalty = db.Column(db.Float)
    innovativeness = db.Column(db.Float)
    score = db.Column(db.Float)

class Monarch(db.Model):
    __tablename__ = "monarch"
    id = db.Column(db.Integer, primary_key = True)
    #TODO
