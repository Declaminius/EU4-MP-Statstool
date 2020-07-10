from statstool_web import db
import enum
from colour import Color
from sqlalchemy_utils import ColorType

class MyEnum(enum.Enum):
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

savegame_goods_produced = db.Table('savegame_goods_produced',
    db.Column('savegame_id', db.Integer, db.ForeignKey('savegame.id')),
    db.Column('trade_good_name', db.String, db.ForeignKey('trade_good.name')),
    db.Column('amount', db.Float, default = 0)
)

nation_data = db.Table('nation_data',
    db.Column('nation_tag', db.String(3), db.ForeignKey('nation.tag')),
    db.Column('data_id', db.Integer, db.ForeignKey('data.id'))
)

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
    db.Column('trade_good_name', db.String, db.ForeignKey('trade_good.name')),
    db.Column('amount', db.Float, default = 0)
)

# data_points_spent = db.Table('data_points_spent',
#     db.Column('data_id', db.Integer, db.ForeignKey('data.id')),
#     db.Column('point_id', db.Integer, db.ForeignKey('points_spent.id')),
#     db.Column('point_category', db.Integer, db.ForeignKey('points_spent.category')),
#     db.Column('amount', db.Float, default = 0)
# )

data_income_per_year = db.Table('data_income_per_year',
    db.Column('data_id', db.Integer, db.ForeignKey('data.id')),
    db.Column('year', db.Integer, db.ForeignKey('year.year')),
    db.Column('amount', db.Float, default = 0)
)

class Savegame(db.Model):
    __tablename__ = 'savegame'
    id = db.Column(db.Integer, primary_key = True)
    year = db.Column(db.Integer, default = None)
    file = db.Column(db.String(120), nullable = False)
    nations = db.relationship("Nation", secondary = savegame_nations)
    player_nations = db.relationship("Nation", secondary = savegame_player_nations)
    total_goods_produced = db.relationship("TradeGood", secondary = savegame_goods_produced)

class Nation(db.Model):
    __tablename__ = 'nation'
    tag = db.Column(db.String(3), primary_key = True)
    name = db.Column(db.String)
    color = db.Column(ColorType)
    data = db.relationship("Data", secondary = nation_data)

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
    #points_spent = db.relationship("PointsSpent", secondary = data_points_spent)
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
    name = db.Column(db.String, primary_key = True)

class PointsSpent(db.Model):
    __tablename__ = 'points_spent'
    id = db.Column(db.Integer, primary_key = True)
    category = db.Column(db.Enum, primary_key = True)
    name = db.Column(db.Integer, default = '?')

class Year(db.Model):
    __tablename__ = 'year'
    year = db.Column(db.Integer, primary_key = True)
