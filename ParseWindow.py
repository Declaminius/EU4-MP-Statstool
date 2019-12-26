# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:21:17 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
import time
import parserfunctions as parser

icon_dir = "files/attack_move.png"

class ParseWindow(Widgets.QWidget):
	switch_back = Core.pyqtSignal()
	switch_edit_nations = Core.pyqtSignal(bool)
	switch_configure_nations = Core.pyqtSignal()
	switch_main_window = Core.pyqtSignal()
	
	def __init__(self, savegame_list):
		super().__init__()
		self.label = Widgets.QLabel(self)
		self.setGeometry(0, 30, 500, 500)
		self.setWindowTitle("Decla's Stats-Tool")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.savegame_list = savegame_list
		self.initMe()
		self.initLayout()

	def initMe(self):

		self.old_nations_list = ["CAS", "ENG", "MOS", "ODA", "POL", "SWE", "BRA", "LAN", "C00", "TUS"]
		self.new_nations_list = ["SPA", "GBR", "RUS", "JAP", "PLC", "SCA", "PRU", "TUS", "TEX", "ITA"]
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
		self.add_button = Widgets.QPushButton("Add Nation", self)
		self.add_button.released.connect(self.add_nation)
		self.remove_button = Widgets.QPushButton("Remove Nation", self)
		self.remove_button.released.connect(self.remove_nation)
		self.remove_all_button = Widgets.QPushButton("Remove All", self)
		self.remove_all_button.released.connect(self.remove_all)
		self.configure_nation_formations_button = Widgets.QPushButton("Configure Nation Formations", self)
		self.configure_nation_formations_button.released.connect(self.configure_nation_formations)
		self.old_version_checkbox = Widgets.QCheckBox("1.25", self)
		self.old_version_checkbox.setChecked(False)


		self.groupBox = Widgets.QGroupBox("Nation Selection Type", self)
		self.was_player_button = Widgets.QRadioButton("Was Player")
		self.all_nations_button = Widgets.QRadioButton("All Nations")

		self.was_player_button.setChecked(True)
		self.playertags_table = Widgets.QTableWidget()
		self.playertags_table.setColumnCount(2)
		self.playertags_table.setHorizontalHeaderLabels(["Old Nations", "New Nations"])
		self.playertags_table.setRowCount(max(len(self.savegame_list[0].playertags), len(self.savegame_list[1].playertags)))

		j = 1
		for savegame in self.savegame_list:
			j += 1
			for i, x in zip(range(len(savegame.playertags)), savegame.playertags):
				item = Widgets.QTableWidgetItem()
				item.setData(Core.Qt.DisplayRole, x)
				item.setFlags(Core.Qt.ItemIsEnabled)
				self.playertags_table.setItem(i-1, j, item)
			
		vbox = Widgets.QVBoxLayout()
		vbox.addWidget(self.was_player_button)
		vbox.addWidget(self.all_nations_button)
		vbox.addStretch(1)
		self.groupBox.setLayout(vbox)
		self.pbar = Widgets.QProgressBar(self)
		self.pbar.setMinimum(0)
		self.pbar.setMaximum(1000)
		self.plabel = Widgets.QLabel("", self)

	def initLayout(self):
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
		grid.addWidget(self.old_version_checkbox, 0, 0)
		grid.addWidget(self.create_button, 0, 1)
		grid.addWidget(self.pbar, 1, 1)
		grid.addWidget(self.back_button, 1, 0)
		grid.addWidget(self.plabel, 2, 1)
		vbox.addLayout(grid)
		vbox.addWidget(self.label)
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
		self.savegame_list[0].playertags = []
		self.savegame_list[1].playertags = []
		self.playertags_table.clear()
		self.playertags_table.setHorizontalHeaderLabels(["Old Nations", "New Nations"])
		self.remove_all_button.setEnabled(False)
		self.remove_button.setEnabled(False)


	def create_statistic(self):
		for savegame in self.savegame_list[:2]:
			if savegame.data_flag:
				with open (savegame.file) as savefile:
					content = savefile.read()
					savegame.datasets, savegame.year, savegame.total_trade_goods,\
					savegame.sorted_tag_list, savegame.income_tag_list, savegame.income_info_list,\
					savegame.income_x_data, savegame.income_y_data, savegame.player_tag_indizes,\
					savegame.color_dict, savegame.army_battle_list, savegame.navy_battle_list,\
					savegame.province_stats_list, savegame.great_power_list,\
					savegame.trade_stats_list, savegame.subject_dict, savegame.hre_reformlevel,\
					savegame.trade_port_dict = eval(content)[-1]
			else:
				start = time.process_time()
				print("Start:", start)
				savegame.datasets, savegame.year, savegame.total_trade_goods, savegame.sorted_tag_list,\
				savegame.income_tag_list, savegame.income_info_list, savegame.income_x_data,\
				savegame.income_y_data, savegame.player_tag_indizes, savegame.color_dict,\
				savegame.army_battle_list, savegame.navy_battle_list, savegame.province_stats_list,\
				savegame.great_power_list, savegame.trade_stats_list, savegame.subject_dict,\
				savegame.hre_reformlevel, savegame.trade_port_dict, savegame.war_list,\
				savegame.war_dict, savegame.tech_dict = parser.parse(savegame.file, self.savegame_list, 
														 self.formable_nations_dict, self.all_nations_button.isChecked(), self.pbar, self.plabel, self.old_version_checkbox.isChecked())
				end = time.process_time()
				print("End:", end)
				print("Time elapsed:", end - start)

			savegame.great_power_y, savegame.great_power_x = parser.sort_two_lists(savegame.datasets[3], savegame.datasets[1])
			savegame.effective_development_y, savegame.effective_development_x = parser.sort_two_lists(savegame.datasets[2], savegame.datasets[1])
			savegame.income_y, savegame.income_x = parser.sort_two_lists(savegame.datasets[6], savegame.datasets[1])
			savegame.manpower_y, savegame.manpower_x = parser.sort_two_lists(savegame.datasets[8], savegame.datasets[7])
			savegame.dummy, savegame.manpower_table = parser.sort_two_lists(savegame.datasets[6], savegame.datasets[7])
			savegame.max_manpower_y, savegame.max_manpower_x = parser.sort_two_lists(savegame.datasets[8], savegame.datasets[1])
			savegame.table_y, savegame.table_x = parser.sort_two_lists(savegame.datasets[3], savegame.datasets[2])
			savegame.tm_y, savegame.tm_x = parser.sort_two_lists(savegame.datasets[6], savegame.datasets[8])
			savegame.losses_list = [savegame.datasets[1]]

			savegame.goods = savegame.datasets[10]
			for i in range(8):
				savegame.losses_list.append([])
			for losses in savegame.datasets[9]:
				savegame.losses_list[1].append(losses[0] + losses[1]) # Infantry
				savegame.losses_list[2].append(losses[3] + losses[4]) # Cavalry
				savegame.losses_list[3].append(losses[0] + losses[1] + losses[3] + losses[4]) # Inf + Cav
				savegame.losses_list[4].append(losses[6] + losses[7]) # Artillery
				savegame.losses_list[5].append(losses[0] + losses[3] + losses[6]) # Combat
				savegame.losses_list[6].append(losses[1] + losses[4] + losses[7]) # Attrition
				savegame.losses_list[7].append(losses[0] + losses[1] + losses[3] + losses[4] + losses[6] + losses[7]) # Total
				savegame.losses_list[8].append(int((losses[0] + losses[1] + losses[3] + losses[4] + losses[6] + losses[7]) / (int(savegame.year)-1445))) # Per Year
			indexes = []
			for i in range(len(savegame.losses_list[0])):
				indexes.append(i)
			indexes.sort(key=savegame.losses_list[7].__getitem__)
			savegame.sorted_losses_list = []
			for losses in savegame.losses_list:
				savegame.sorted_losses_list.append(list(map(losses.__getitem__, indexes)))

			savegame.stats_dict = dict(zip(savegame.datasets[1], zip([savegame.datasets[(x+2)][i] for x in range(len(savegame.datasets)-2)] for i in range(len(savegame.datasets[1])))))
			for key, value in zip(savegame.stats_dict, savegame.stats_dict.values()):
				savegame.stats_dict[key] = value[0]
			savegame.legend = ["effective_development", "great_power_score", "development",
					  "navy_strength", "income", "current_manpower", "max_manpower", "losses",
					  "trade goods"]
		self.switch_main_window.emit()