# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:45:00 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
import parserfunctions as parser
icon_dir = "files/attack_move.png"

class TableWindow(Widgets.QMainWindow):
	switch_nation_selecter = Core.pyqtSignal(list)
	switch_commander_selecter = Core.pyqtSignal(list)
	switch_war_selecter = Core.pyqtSignal(list)
	switch_province_filter = Core.pyqtSignal(int, list)
	
	def __init__(self, savegame_list, data, title = "Table"):
		super().__init__()
		self.data = data
		self.savegame_list = savegame_list
		self.setGeometry(0, 30, 1920, 800)
		self.setWindowTitle(title)
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.table = Widgets.QTableWidget()
		self.setCentralWidget(self.table)

		if data == self.savegame_list[1].army_battle_list:
			self.armyTable(data)
			self.menu()
			self.header(9,12,19)

		if data == self.savegame_list[1].navy_battle_list:
			self.navyTable(data)
			self.menu()
			self.header(19,24,30)

		if data == self.savegame_list[1].province_stats_list:
			self.provinceTable(data)
			self.province_menu()

		if len(data[0]) == 8:
			self.warLossesTable(data)

		if len(data[0]) == 9:
			self.warTotalLossesTable(data)
			self.war_menu()

	def menu(self):
		self.menu = self.menuBar()
		self.filter_menu = self.menu.addMenu("&Filter by...")
		self.war_filter = Widgets.QAction("Filter by war", self)
		self.war_filter.triggered.connect(self.war_table)
		self.war_filter.setShortcut("Ctrl+F")
		self.commander_filter = Widgets.QAction("Filter by commander", self)
		self.commander_filter.triggered.connect(self.filter_commander)
		self.nation_filter = Widgets.QAction("Filter by Nation", self)
		self.nation_filter.triggered.connect(self.filter_nations)
		self.player_nation_filter = Widgets.QAction("Filter by Player Nations", self)
		self.player_nation_filter.triggered.connect(self.player_filter_nations)
		self.show_all = Widgets.QAction("Show All", self)
		self.show_all.triggered.connect(self.show_all_battles)
		self.filter_menu.addAction(self.war_filter)
		self.filter_menu.addAction(self.commander_filter)
		self.filter_menu.addAction(self.nation_filter)
		self.filter_menu.addAction(self.player_nation_filter)
		self.filter_menu.addAction(self.show_all)

	def province_menu(self):
		self.menu = self.menuBar()
		self.filter_menu = self.menu.addMenu("&Filter by...")
		self.nation_filter = Widgets.QAction("Filter by Nation", self)
		self.nation_filter.triggered.connect(self.filter_nations)
		self.trade_node_filter = Widgets.QAction("Filter by Trade Node", self)
		self.trade_node_filter.triggered.connect(self.filter_trade_node)
		self.culture_filter = Widgets.QAction("Filter by Culture", self)
		self.culture_filter.triggered.connect(self.filter_culture)
		self.religion_filter = Widgets.QAction("Filter by Religion", self)
		self.religion_filter.triggered.connect(self.filter_religion)
		self.trade_good_filter = Widgets.QAction("Filter by Trade Good", self)
		self.trade_good_filter.triggered.connect(self.filter_trade_good)
		self.area_filter = Widgets.QAction("Filter by Area", self)
		self.area_filter.triggered.connect(self.filter_area)
		self.region_filter = Widgets.QAction("Filter by Region", self)
		self.region_filter.triggered.connect(self.filter_region)
		self.superregion_filter = Widgets.QAction("Filter by Superregion", self)
		self.superregion_filter.triggered.connect(self.filter_superregion)
		self.show_all = Widgets.QAction("Show All", self)
		self.show_all.triggered.connect(self.show_all_provinces)
		self.filter_menu.addAction(self.nation_filter)
		self.filter_menu.addAction(self.trade_node_filter)
		self.filter_menu.addAction(self.culture_filter)
		self.filter_menu.addAction(self.religion_filter)
		self.filter_menu.addAction(self.trade_good_filter)
		self.filter_menu.addAction(self.area_filter)
		self.filter_menu.addAction(self.region_filter)
		self.filter_menu.addAction(self.superregion_filter)
		self.filter_menu.addAction(self.show_all)

	def war_menu(self):
		self.menu = self.menuBar()
		self.war_menu = self.menu.addMenu("Show all")
		self.explain_menu = self.menu.addMenu("Doubleclick war to see individual stats")
		self.war_action = Widgets.QAction("Show all", self)
		self.war_action.triggered.connect(self.show_all)
		self.war_menu.addAction(self.war_action)

	def armyTable(self, data):
		self.table.setSortingEnabled(True)
		self.table.setRowCount(len(data))
		self.table.setSizeAdjustPolicy(Widgets.QAbstractScrollArea.AdjustToContents)
		self.table.setColumnCount(20)
		self.table.setHorizontalHeaderLabels(
			["Province", "Winner", "Date", "Cavalry", "Artillery", "Infantry", "Total", "Losses", "Country",
			 "Commander", "Cavalry", "Artillery", "Infantry", "Total", "Losses", "Country", "Commander",
			 "Total Units", "Total Losses", "War"])

		if not data:
			return []

		for a, b in zip(range(len(data)), data):
			for c, d in zip(range(len(b)), b):
				item = Widgets.QTableWidgetItem()
				item.setData(Core.Qt.DisplayRole, d)
				self.table.setItem(a, c, item)
		self.table.resizeColumnsToContents()

		self.multiple_column_colors([6,13], data)
		self.multiple_column_colors([7,14], data)
		self.multiple_column_colors([17], data)
		self.multiple_column_colors([18], data)
		for a, b in zip(range(len(data)), data):
			for x in (0,7):
				self.table.item(a, 5+x).setBackground(Gui.QColor("royalblue"))
				self.table.item(a, 3+x).setBackground(Gui.QColor("saddlebrown"))
				self.table.item(a, 4+x).setBackground(Gui.QColor("dimgray"))

		for x in range(len(data)):
			for y in [8,15]:
				if self.table.item(x, y).text() in self.savegame_list[1].color_dict:
					self.table.item(x, y).setBackground(Gui.QColor(self.savegame_list[1].color_dict[self.table.item(x, y).text()]))
			if self.table.item(x, 1).text() == "Attacker":
				self.table.item(x, 1).setBackground(Gui.QColor("green"))
				self.table.item(x, 9).setBackground(Gui.QColor("green"))
				self.table.item(x, 16).setBackground(Gui.QColor("red"))
			if self.table.item(x, 1).text() == "Defender":
				self.table.item(x, 1).setBackground(Gui.QColor("red"))
				self.table.item(x, 9).setBackground(Gui.QColor("red"))
				self.table.item(x, 16).setBackground(Gui.QColor("green"))

	def navyTable(self, data):
		self.table.setSortingEnabled(True)
		self.table.setRowCount(len(data))
		self.table.setSizeAdjustPolicy(Widgets.QAbstractScrollArea.AdjustToContents)
		self.table.setColumnCount(22)
		self.table.setHorizontalHeaderLabels(
			["Province", "Winner", "Date", "Galleys", "Light Ships", "Heavy Ships", "Transports", "Total", "Losses",
			 "Country", "Commander", "Galleys", "Light Ships", "Heavy Ships", "Transports", "Total", "Losses", "Country",
			 "Commander", "Total Units", "Total Losses", "War"])

		if not data:
			return []

		for a, b in zip(range(len(data)), data):
			for c, d in zip(range(len(b)), b):
				item = Widgets.QTableWidgetItem()
				item.setData(Core.Qt.DisplayRole, d)
				self.table.setItem(a, c, item)
		self.table.resizeColumnsToContents()

		self.multiple_column_colors([7,15], data)
		self.multiple_column_colors([8,16], data)
		self.multiple_column_colors([19], data)
		self.multiple_column_colors([20], data)

		for a, b in zip(range(len(data)), data):
			for x in (0,8):
				self.table.item(a, 3+x).setBackground(Gui.QColor("khaki"))
				self.table.item(a, 4+x).setBackground(Gui.QColor("mediumturquoise"))
				self.table.item(a, 5+x).setBackground(Gui.QColor("silver"))
				self.table.item(a, 6+x).setBackground(Gui.QColor("sienna"))

		for x in range(len(data)):
			for y in [9,17]:
				if self.table.item(x, y).text() in self.savegame_list[1].color_dict:
					self.table.item(x, y).setBackground(Gui.QColor(self.savegame_list[1].color_dict[self.table.item(x, y).text()]))
			if self.table.item(x, 1).text() == "Attacker":
				self.table.item(x, 1).setBackground(Gui.QColor("green"))
			if self.table.item(x, 1).text() == "Defender":
				self.table.item(x, 1).setBackground(Gui.QColor("red"))

	def provinceTable(self, data):
		data = data[:]
		self.table.setSortingEnabled(True)
		self.table.setRowCount(0)
		self.table.setRowCount(len(data))
		self.table.setSizeAdjustPolicy(Widgets.QAbstractScrollArea.AdjustToContents)
		self.table.setColumnCount(15)
		self.table.setHorizontalHeaderLabels(
			["Province ID", "Name", "Owner",  "Base Tax", "Base Production", "Base Manpower",
			 "Development", "Trade Power", "Trade Node", "Culture", "Religion", "Trade Good", "Area", "Region", "Superregion"])

		if not data:
			return []

		for a, province in zip(range(len(data)), data):
			for c, d in zip(range(len(province)), province):
				item = Widgets.QTableWidgetItem()
				item.setData(Core.Qt.DisplayRole, d)
				self.table.setItem(a, c, item)

		self.table.resizeColumnsToContents()
		self.multiple_column_colors([7], data)
		self.multiple_column_colors([6], data)
		self.multiple_column_colors([3,4,5], data)

		for x in range(len(data)):
			if self.table.item(x, 2).text() in self.savegame_list[1].color_dict:
				self.table.item(x, 2).setBackground(Gui.QColor(self.savegame_list[1].color_dict[self.table.item(x, 2).text()]))

	def warLossesTable(self, data, title = "No Title"):
		self.setWindowTitle(title)
		self.table.setSortingEnabled(True)
		self.table.setRowCount(len(data))
		self.table.setSizeAdjustPolicy(Widgets.QAbstractScrollArea.AdjustToContents)
		self.table.setColumnCount(8)
		self.table.setHorizontalHeaderLabels(
			["Nation", "War Contribution", "Infantry", "Cavalry", "Artillery", "Combat", "Attrition", "Total"])

		if not data:
			return []

		for a, b in zip(range(len(data)), data):
			for c, d in zip(range(len(b)), b):
				item = Widgets.QTableWidgetItem()
				item.setData(Core.Qt.DisplayRole, d)
				self.table.setItem(a, c, item)
		self.table.resizeColumnsToContents()

		self.multiple_column_colors([5,6,7], data)
		self.multiple_column_colors([1], data)
		for a, b in zip(range(len(data)), data):
			self.table.item(a, 2).setBackground(Gui.QColor("royalblue"))
			self.table.item(a, 3).setBackground(Gui.QColor("saddlebrown"))
			self.table.item(a, 4).setBackground(Gui.QColor("dimgray"))

		for x in range(len(data)):
			if self.table.item(x, 0).text() in self.savegame_list[1].color_dict:
				self.table.item(x, 0).setBackground(Gui.QColor(self.savegame_list[1].color_dict[self.table.item(x, 0).text()]))

	def warTotalLossesTable(self, data):
		self.table.setSortingEnabled(True)
		self.table.setRowCount(len(data))
		self.table.setSizeAdjustPolicy(Widgets.QAbstractScrollArea.AdjustToContents)
		self.table.setColumnCount(9)
		self.table.setHorizontalHeaderLabels(
			["War", "Attacker", "Defender", "Infantry", "Cavalry", "Artillery", "Combat", "Attrition", "Total"])

		if not data:
			return []

		for a, b in zip(range(len(data)), data):
			for c, d in zip(range(len(b)), b):
				item = Widgets.QTableWidgetItem()
				item.setData(Core.Qt.DisplayRole, d)
				self.table.setItem(a, c, item)
		self.table.resizeColumnsToContents()

		self.multiple_column_colors([6,7,8], data)
		for a, b in zip(range(len(data)), data):
			self.table.item(a, 3).setBackground(Gui.QColor("royalblue"))
			self.table.item(a, 4).setBackground(Gui.QColor("saddlebrown"))
			self.table.item(a, 5).setBackground(Gui.QColor("dimgray"))

		for x in range(len(data)):
			for i in range(1,3):
				if self.table.item(x, i).text() in self.savegame_list[1].color_dict:
					self.table.item(x, i).setBackground(Gui.QColor(self.savegame_list[1].color_dict[self.table.item(x, i).text()]))

	def war_table(self):
		self.switch_war_selecter.emit(self.data)

	def show_all(self):
		self.warTotalLossesTable(self.data)

	def filter_commander(self):
		self.switch_commander_selecter.emit(self.data)

	def filter_nations(self):
		self.switch_nation_selecter.emit(self.data)

	def player_filter_nations(self):
		if self.data == self.savegame_list[1].army_battle_list:
			new_data = [battle for battle in self.data if (battle[8] in self.savegame_list[1].playertags or battle[15] in self.savegame_list[1].playertags)]
			self.armyTable(new_data)
		if self.data == self.savegame_list[1].navy_battle_list:
			new_data = [battle for battle in self.data if (battle[9] in self.savegame_list[1].playertags or battle[17] in self.savegame_list[1].playertags)]
			self.navyTable(new_data)

	def show_all_battles(self):
		if self.data == self.savegame_list[1].army_battle_list:
			self.armyTable(self.data)
		if self.data == self.savegame_list[1].navy_battle_list:
			self.navyTable(self.data)

	def show_all_provinces(self):
		self.provinceTable(self.data)

	def filter_trade_node(self):
		self.switch_province_filter.emit(7, self.data)

	def filter_culture(self):
		self.switch_province_filter.emit(8, self.data)

	def filter_religion(self):
		self.switch_province_filter.emit(9, self.data)

	def filter_trade_good(self):
		self.switch_province_filter.emit(10, self.data)	

	def filter_area(self):
		self.switch_province_filter.emit(11, self.data)

	def filter_region(self):
		self.switch_province_filter.emit(12, self.data) 

	def filter_superregion(self):
		self.switch_province_filter.emit(13, self.data)

	def header(self, x, y, z):
		self.header_label1 = Widgets.QLabel("Attacker")
		self.header_label2 = Widgets.QLabel("Defender")
		self.layout = Widgets.QHBoxLayout()
		self.layout.addStretch(x)
		self.layout.addWidget(self.header_label1)
		self.layout.addStretch(y)
		self.layout.addWidget(self.header_label2)
		self.layout.addStretch(z)
		self.header = Widgets.QWidget()
		self.header.setLayout(self.layout)
		self.dock = Widgets.QDockWidget()
		self.dock.setTitleBarWidget(self.header)
		self.addDockWidget(Core.Qt.TopDockWidgetArea, self.dock)

	def multiple_column_colors(self, columns, data):
		color = parser.colormap([int(a[x]) for a in data for x in columns], 0, 255)
		for a in range(len(data)):
			for x, b in zip(columns, color):
				self.table.item(a, x).setBackground(Gui.QColor(*b))
			for x in columns:
				del color[0]