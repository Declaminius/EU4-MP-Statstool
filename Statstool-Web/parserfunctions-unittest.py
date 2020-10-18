from statstool_web.parserfunctions import *
import unittest
from test_string import *

content = 	"""target_merge_province=621
	under_construction_queued=2
}
unit_templates={
	id={
		id=78
		type=57
	}
	target_merge_province=97
	under_construction_queued=3
}
unit_templates={
	id={
		id=81
		type=57
	}
	target_merge_province=4383
	under_construction_queued=1
}
production_leader_tag={
	--- MNG FRA TUR TUR SWE RUS MNG PLC SWE TUR RUS GBR AVA MNG MNG VIJ YEM VIJ C02 C01 C03 MUG PLC AYU PLC YEM NED MUG VIJ --- C07
}
dynamic_countries={
	T00 C00 C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C11 C12
}
tradegoods_total_produced={
	0.000 385.933 83.951 103.439 278.771 168.758 80.112 97.314 116.123 62.126 43.365 143.488 31.087 31.745 23.589 37.247 76.855 24.680 85.194 53.719 24.534 25.129 73.818 24.997 44.688 249.510 27.877 19.565 68.555 62.543 0.000 157.925
}
change_price={
	nogoods={
		current_price=1.000
	}
	grain={
		current_price=2.000
		change_price={
			key="COLUMBIAN_EXCHANGE"
			value=-0.200
			expiry_date=1821.1.2
		}
	}
	wine={
		current_price=2.500
	}
	wool={
		current_price=2.000
		change_price={"""

info = test_string
tag = "TEST"
ae = compile("modifier=\"aggressive_expansion\"[^}]+?current_opinion=(-\d+.\d+)", DOTALL)
nation_data = {}
parse_relations(info, tag, ae, nation_data)


regiment_strength = compile("strength=(\d.\d+)")

parse_regiments(test_string2, tag, regiment_strength, nation_data)

parse_ships(test_string2, tag, nation_data)


parse_production_leader(content, 1)
