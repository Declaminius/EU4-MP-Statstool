# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:47:44 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
icon_dir = "files/attack_move.png"

class NationSelecter(Widgets.QWidget):
	update_table = Core.pyqtSignal(str, list)
	
	def __init__(self, data, savegame_list):
		super().__init__()
		self.data = data
		self.savegame_list = savegame_list
		self.setGeometry(0, 30, 600, 100)
		self.setWindowTitle("Select Nation")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.select_nation = Widgets.QComboBox(self)
		for tag in self.savegame_list[1].tag_list:
			self.select_nation.addItem(tag)
		self.select_nation.move(100,40)
		self.select_nation.activated[str].connect(self.filter_nation)
		self.show()

	def filter_nation(self, tag):
		if self.data == self.savegame_list[1].army_battle_list:
			new_data = [battle for battle in self.data if (battle[8] == tag or battle[15] == tag)]
			self.update_table.emit("army", new_data)
		if self.data == self.savegame_list[1].navy_battle_list:
			new_data = [battle for battle in self.data if (battle[9] == tag or battle[17] == tag)]
			self.update_table.emit("navy", new_data)
		if self.data == self.savegame_list[1].province_stats_list:
			new_data = [province for province in self.data if (province[2] == tag)]
			self.update_table.emit("province", new_data)
		self.close()


class WarSelecter(Widgets.QWidget):
	update_table = Core.pyqtSignal(str, list)
	
	def __init__(self, data, savegame_list):
		super().__init__()
		self.data = data
		self.savegame_list = savegame_list
		self.setGeometry(0, 30, 600, 100)
		self.setWindowTitle("Select War")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.select_war = Widgets.QComboBox(self)
		if len(data[0]) == 10:
			real_war_list = sorted(d[0] for d in data)
		else:
			real_war_list = sorted([war for war in self.savegame_list[1].war_list if war in [war[-1] for war in self.data]])
		for war in real_war_list:
			self.select_war.addItem(war)
		self.select_war.move(100,40)
		self.select_war.activated[str].connect(self.filter_war)
		self.show()

	def filter_war(self, war):
		new_data = [battle for battle in self.data if battle[-1] == war]
		self.close()
		if self.data == self.savegame_list[1].army_battle_list:
			self.update_table.emit("army", new_data)
		if self.data == self.savegame_list[1].navy_battle_list:
			self.update_table.emit("navy", new_data)
		if len(self.data[0]) == 10:
			self.update_table.emit("province", self.savegame_list[1].war_dict[war])


class CommanderSelecter(Widgets.QWidget):
	update_table = Core.pyqtSignal(str, list)
	
	def __init__(self, data, savegame_list):
		super().__init__()
		self.data = data
		self.savegame_list = savegame_list
		self.setGeometry(0, 30, 600, 100)
		self.setWindowTitle("Select Commander")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.select_commander = Widgets.QComboBox(self)
		if self.data == self.savegame_list[1].army_battle_list:
			commander_list = sorted(set([battle[9] for battle in self.data] + [battle[16] for battle in self.data]))
		if self.data == self.savegame_list[1].navy_battle_list:
			commander_list = sorted(set([battle[10] for battle in self.data] + [battle[18] for battle in self.data]))
		for commander in commander_list:
			self.select_commander.addItem(commander)
		self.select_commander.move(100,40)
		self.select_commander.activated[str].connect(self.filter_commander)
		self.show()

	def filter_commander(self, commander):
		self.close()
		if self.data == self.savegame_list[1].army_battle_list:
			new_data = [battle for battle in self.data if (battle[9] == commander or battle[16] == commander)]
			self.update_table.emit("army", new_data)
		if self.data == self.savegame_list[1].navy_battle_list:
			new_data = [battle for battle in self.data if (battle[10] == commander or battle[18] == commander)]
			self.update_table.emit("navy", new_data)