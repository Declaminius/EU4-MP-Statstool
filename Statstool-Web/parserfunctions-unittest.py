from statstool_web.parserfunctions import *
import unittest
from test_string import *



info = test_string
tag = "TEST"
ae = compile("modifier=\"aggressive_expansion\"[^}]+?current_opinion=(-\d+.\d+)", DOTALL)
nation_data = {}
parse_relations(info, tag, ae, nation_data)


regiment_strength = compile("strength=(\d.\d+)")

parse_regiments(test_string2, tag, regiment_strength, nation_data)

parse_ships(test_string2, tag, nation_data)

print(nation_data)
