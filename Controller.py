# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 14:09:26 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtCore as Core

from SetupWindow import SetupWindow
from ParseWindow import ParseWindow
from EditNations import EditNations
from ConfigureNations import ConfigureNations
from MainWindow import MainWindow
from TableWindow import TableWindow
from Overview import Overview
from Selecter import NationSelecter, WarSelecter, CommanderSelecter
from ProvinceFilter import ProvinceFilter

class Controller:

	def __init__(self):
		self.setup_window = SetupWindow()
		self.setup_window.switch_window.connect(self.show_parse_window)
		self.setup_window.show()

	def show_parse_window(self):
		try:
			self.setup_window.close()
			self.parse_window = ParseWindow(self.setup_window.savegame_list)
			self.parse_window.switch_back.connect(self.back_to_setup)
			self.parse_window.switch_edit_nations.connect(self.show_edit_nations)
			self.parse_window.switch_configure_nations.connect(self.show_configure_nations)
			self.parse_window.switch_main_window.connect(self.show_main_window)
			self.parse_window.show()
		except AttributeError as err:
			self.setup_window.show()
			self.setup_window.status.showMessage("Error:{}\nSelect two Savegames".format(err))

	def back_to_setup(self):
		self.parse_window.close()
		self.setup_window.savegame_list = [[],[]]
		self.setup_window.line1.setText("")
		self.setup_window.line2.setText("")
		self.setup_window.show()

	def show_edit_nations(self, b):
		self.edit_nations_window = EditNations(b, self.parse_window.savegame_list)
		self.edit_nations_window.set_playertags.connect(self.set_playertags)
		self.edit_nations_window.show()

	def set_playertags(self):
		self.parse_window.playertags_table.clear()
		self.parse_window.playertags_table.setRowCount(max(len(self.parse_window.savegame_list[0].playertags),
													 len(self.parse_window.savegame_list[1].playertags)))
		j = 1
		for sg in self.parse_window.savegame_list:
			j += 1
			for i, x in zip(range(len(sg.playertags)), sg.playertags):
				item = Widgets.QTableWidgetItem()
				item.setData(Core.Qt.DisplayRole, x)
				item.setFlags(Core.Qt.ItemIsEnabled)
				self.parse_window.playertags_table.setItem(i-1, j, item)
		self.parse_window.playertags_table.setHorizontalHeaderLabels(["Savegame 1", "Savegame 2"])
		if self.parse_window.savegame_list[0].playertags + self.parse_window.savegame_list[1].playertags:
			self.parse_window.remove_all_button.setEnabled(True)
			self.parse_window.remove_button.setEnabled(True)
		else:
			self.parse_window.remove_all_button.setEnabled(False)
			self.parse_window.remove_button.setEnabled(False)

	def show_configure_nations(self):
		self.configure_window = ConfigureNations(self.parse_window.savegame_list, self.parse_window.old_nations_list,
										   self.parse_window.new_nations_list, self.parse_window.formable_nations_dict)
		self.configure_window.set_nation_formations.connect(self.set_nation_formations)
		self.configure_window.show()

	def set_nation_formations(self, formable_nations_dict):
		self.parse_window.formable_nations_dict = formable_nations_dict
		for label in self.parse_window.label_list:
			label.clear()
		for (key, value), label in zip(self.parse_window.formable_nations_dict.items(), self.parse_window.label_list):
			label.setText("{0} {1} {2}".format(value, chr(10230), key))

	def show_main_window(self):
		self.parse_window.close()
		self.main_window = MainWindow(self.parse_window.savegame_list, self.parse_window.formable_nations_dict)
		self.main_window.main.switch_table_window.connect(self.show_table_window)
		self.main_window.main.back_to_parse_window.connect(self.back_to_parse_window)
		self.main_window.main.switch_overview_window.connect(self.show_overview_window)
		self.main_window.main.switch_error_window.connect(self.show_error_window)
		self.main_window.show()

	def show_table_window(self, data, title):
		self.table_window = TableWindow(self.parse_window.savegame_list, data, title)
		self.table_window.switch_nation_selecter.connect(self.show_nation_selecter)
		self.table_window.switch_commander_selecter.connect(self.show_commander_selecter)
		self.table_window.switch_war_selecter.connect(self.show_war_selecter)
		self.table_window.switch_province_filter.connect(self.show_province_filter)
		self.table_window.show()

	def show_nation_selecter(self):
		self.nation_select_window = NationSelecter(self.data, self.parse_window.savegame_list)
		self.nation_select_window.update_table.connect(self.update_table)
		self.nation_select_window.show()

	def show_commander_selecter(self):
		self.commander_select_window = CommanderSelecter(self.data, self.parse_window.savegame_list)
		self.commander_select_window.update_table.connect(self.update_table)
		self.commander_select_window.show()

	def show_war_selecter(self):
		self.war_select_window = WarSelecter(self.data, self.parse_window.savegame_list)
		self.war_select_window.update_table.connect(self.update_table)
		self.war_select_window.show()

	def show_province_filter(self, number, data):
		self.province_filter = ProvinceFilter(number, data)
		self.province_filter.update_table.connect(self.update_table)
		self.province_filter.show()

	def update_table(self, category, data):
		if category == "army":
			self.table_window.armyTable(data)
		if category == "navy":
			self.table_window.navyTable(data)
		if category == "province":
			self.table_window.provinceTable(data)

	def show_overview_window(self, title, columns, column_count, header_labels, data):
		self.overview_window = Overview(self.parse_window.savegame_list, title, columns, column_count, header_labels, data)
		self.overview_window.show()

	def show_error_window(self,e):
		self.error_window = ErrorWindow("Something went wrong. Check Nation Formations.\nError: \n{0}".format(e))
		self.error_window.show()

	def back_to_parse_window(self):
		self.main_window.close()
		self.parse_window.show()
