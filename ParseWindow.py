# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:21:17 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
import time
from parserfunctions import parse

icon_dir = "files/attack_move.png"

class ParseWindow(Widgets.QWidget):
	switch_back = Core.pyqtSignal()
	switch_edit_nations = Core.pyqtSignal(bool)
	switch_configure_nations = Core.pyqtSignal()
	switch_main_window = Core.pyqtSignal()

	def __init__(self, savegame_list, playertags):
		super().__init__()
		self.savegame_list = savegame_list
		self.playertags = playertags
		self.tag_list = self.savegame_list[1].tag_list
		self.old_nations_list = ["RVA", "ORL"]
		self.new_nations_list = ["WES", "FRA"]
		self.playertags.remove("HUN")
		self.playertags.remove("CAS")
		self.playertags.remove("SPA")
		self.playertags.remove("MOS")
		self.playertags.remove("CRI")
		self.playertags.remove("MCM")
		self.formable_nations_dict = dict(zip(self.new_nations_list, self.old_nations_list))

		self.first_label = Widgets.QLabel("Standard Nation Formations:", self)
		self.label_list = []
		for i in range(20):
			label = Widgets.QLabel("", self)
			self.label_list.append(label)
		for (key, value), label in zip(self.formable_nations_dict.items(), self.label_list):
			label.setText("{0} {1} {2}".format(value, chr(10230), key))

		self.create_button = Widgets.QPushButton("Create Statistic", self)
		self.create_button.released.connect(self.create_statistic)
		self.create_button.setShortcut("Ctrl+C")
		self.back_button = Widgets.QPushButton("Back", self)
		self.back_button.released.connect(self.back)
		self.back_button.setShortcut("Ctrl+B")
		self.add_button = Widgets.QPushButton("Add Nation", self)
		self.add_button.released.connect(self.add_nation)
		self.remove_button = Widgets.QPushButton("Remove Nation", self)
		self.remove_button.released.connect(self.remove_nation)
		self.remove_all_button = Widgets.QPushButton("Remove All", self)
		self.remove_all_button.released.connect(self.remove_all)
		self.configure_nation_formations_button = Widgets.QPushButton("Configure Nation Formations", self)
		self.configure_nation_formations_button.released.connect(self.configure_nation_formations)

		self.groupBox = Widgets.QGroupBox("Nation Selection Type", self)
		self.was_player_button = Widgets.QRadioButton("Players only")
		self.all_nations_button = Widgets.QRadioButton("All Nations (use at own risk)")

		self.was_player_button.setChecked(True)
		self.playertags_table = Widgets.QTableWidget()
		self.playertags_table.setColumnCount(1)
		self.playertags_table.setHorizontalHeaderLabels(["Player-Tags"])
		self.playertags_table.setRowCount(len(self.playertags))

		for i in range(len(self.playertags)):
			item = Widgets.QTableWidgetItem()
			item.setData(Core.Qt.DisplayRole, self.playertags[i])
			item.setFlags(Core.Qt.ItemIsEnabled)
			self.playertags_table.setItem(i, 0, item)

		vbox = Widgets.QVBoxLayout()
		vbox.addWidget(self.was_player_button)
		vbox.addWidget(self.all_nations_button)
		vbox.addStretch(1)
		self.groupBox.setLayout(vbox)
		self.pbar = Widgets.QProgressBar(self)
		self.pbar.setMinimum(0)
		self.pbar.setMaximum(1000)
		self.plabel = Widgets.QLabel("", self)
		self.init_ui()

	def init_ui(self):
		self.setGeometry(0, 30, 500, 500)
		self.setWindowTitle("Decla's Stats-Tool")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		hbox = Widgets.QHBoxLayout(self)
		vbox = Widgets.QVBoxLayout()
		vbox.addWidget(self.playertags_table)
		sub_hbox = Widgets.QHBoxLayout()
		sub_hbox.addWidget(self.add_button)
		sub_hbox.addWidget(self.remove_button)
		sub_hbox.addWidget(self.remove_all_button)
		vbox.addLayout(sub_hbox)
		hbox.addLayout(vbox)
		vbox = Widgets.QVBoxLayout()
		vbox.addWidget(self.groupBox)
		vbox.addWidget(self.configure_nation_formations_button)
		vbox.addWidget(self.first_label)
		for label1, label2 in zip(self.label_list[::2], self.label_list[1::2]):
			sub_hbox = Widgets.QHBoxLayout()
			sub_hbox.addWidget(label1)
			sub_hbox.addWidget(label2)
			vbox.addLayout(sub_hbox)
		grid = Widgets.QGridLayout(self)
		grid.addWidget(self.create_button, 0, 1)
		grid.addWidget(self.pbar, 1, 1)
		grid.addWidget(self.back_button, 1, 0)
		grid.addWidget(self.plabel, 2, 1)
		vbox.addLayout(grid)
		hbox.addLayout(vbox)

		self.setLayout(hbox)
		self.show()

	def back(self):
		self.switch_back.emit()

	def add_nation(self):
		self.switch_edit_nations.emit(True)

	def remove_nation(self):
		self.switch_edit_nations.emit(False)

	def configure_nation_formations(self):
		self.switch_configure_nations.emit()

	def remove_all(self):
		self.playertags = []
		self.playertags_table.clear()
		self.playertags_table.setHorizontalHeaderLabels(["Player-Tags"])
		self.playertags_table.setRowCount(1)
		self.remove_all_button.setEnabled(False)
		self.remove_button.setEnabled(False)

	def create_statistic(self):
		for savegame in self.savegame_list[:2]:
			start = time.process_time()
			print("Start:", start)
			savegame.stats_dict, savegame.year, savegame.total_trade_goods, savegame.sorted_tag_list,\
			savegame.income_dict, savegame.color_dict,\
			savegame.army_battle_list, savegame.navy_battle_list, savegame.province_stats_list,\
			savegame.trade_stats_list, savegame.subject_dict,\
			savegame.hre_reformlevel, savegame.trade_port_dict, savegame.war_list,\
			savegame.war_dict, savegame.tech_dict, savegame.monarch_list, self.localisation_dict =\
			parse(savegame.file, self.playertags, self.savegame_list,
			self.formable_nations_dict, self.all_nations_button.isChecked(), self.pbar, self.plabel)
			end = time.process_time()
			print("End:", end)
			print("Time elapsed:", end - start)
		self.switch_main_window.emit()
