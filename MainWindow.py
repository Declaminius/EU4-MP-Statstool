# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:33:53 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core

from Savegame import Savegame
import webbrowser
import copy
from os import makedirs
import matplotlib.pyplot as plt
from parserfunctions import colormap, parse

trade_goods_list = ['', 'Getreide', 'Wein', 'Wolle', 'Tuch', 'Fisch', 'Pelze', 'Salz',
					'Schiffsbedarf', 'Kupfer', 'Gold', 'Eisen', 'Sklaven', 'Elfenbein',
					'Tee', 'Porzellan', 'Gewürze', 'Kaffee', 'Baumwolle', 'Zucker', 'Tabak',
					'Kakao', 'Seide', 'Farbstoffe', 'Tropenholz', 'Vieh', 'Weihrauch', 'Glas',
					'Papier', 'Edelsteine', '', 'Unbekannt']
icon_dir = "files/attack_move.png"

class ShowStats(Widgets.QWidget):
	back_to_parse_window = Core.pyqtSignal()
	change_dir = Core.pyqtSignal()
	switch_table_window = Core.pyqtSignal(list, str)
	switch_overview_window = Core.pyqtSignal(str, list, int, list, dict)
	switch_error_window = Core.pyqtSignal(str)

	def __init__(self, savegame_list, formable_nations_dict):
		super().__init__()
		self.savegame_list = savegame_list
		self.formable_nations_dict = formable_nations_dict
		self.savegame_list.append(Savegame())
		# Create empty Savegame as placeholer for the comparison between Savegame 1 and 2
		self.savegame_list[2].year = str(self.savegame_list[0].year) + " - " + str(self.savegame_list[1].year)

		self.save_figures_box = Widgets.QCheckBox("Save Figures", self)
		self.save_figures_box.setChecked(True)
		self.show_button = Widgets.QPushButton("Show Stats", self)
		self.show_button.released.connect(self.show_stats)
		self.select_all_button = Widgets.QPushButton("Select All", self)
		self.select_all_button.released.connect(self.select_all)
		self.deselect_all_button = Widgets.QPushButton("Deselect All", self)
		self.deselect_all_button.released.connect(self.deselect_all)
		self.close_button = Widgets.QPushButton("Close Stats", self)
		self.close_button.released.connect(self.close_stats)

		self.wars_button = Widgets.QPushButton("Wars", self)
		self.wars_button.released.connect(self.wars)

		self.army_battle_button = Widgets.QPushButton("Army Battles", self)
		self.army_battle_button.released.connect(self.army_battle)

		self.navy_battle_button = Widgets.QPushButton("Navy Battles", self)
		self.navy_battle_button.released.connect(self.navy_battle)

		self.province_list_button = Widgets.QPushButton("Provinces", self)
		self.province_list_button.released.connect(self.provinces)

		self.overview_button = Widgets.QPushButton("Overview Table", self)
		self.overview_button.released.connect(self.overview)

		self.tech_button = Widgets.QPushButton("Tech Table", self)
		self.tech_button.released.connect(self.tech)

		self.adm_points_spent_button = Widgets.QPushButton("Adm-Points Spent Table", self)
		self.adm_points_spent_button.released.connect(self.adm_points_spent)

		self.dip_points_spent_button = Widgets.QPushButton("Dip-Points Spent Table", self)
		self.dip_points_spent_button.released.connect(self.dip_points_spent)

		self.mil_points_spent_button = Widgets.QPushButton("Mil-Points Spent Table", self)
		self.mil_points_spent_button.released.connect(self.mil_points_spent)

		self.total_points_spent_button = Widgets.QPushButton("Total Points Spent Table", self)
		self.total_points_spent_button.released.connect(self.total_points_spent)

		self.upload_button = Widgets.QPushButton("Upload to Abload", self)
		self.upload_button.released.connect(self.upload)

		self.back_button = Widgets.QPushButton("Back", self)
		self.back_button.released.connect(self.back)

		self.initUI()

	def create_groupbox(self, savegame, title, checks, b = True):

		savegame.box_list = []
		savegame.method_list = []

		savegame.development_box = Widgets.QCheckBox("Development", self)
		savegame.box_list.append(savegame.development_box)
		savegame.method_list.append(self.development)

		savegame.income_manpower_box = Widgets.QCheckBox("Income +  Manpower", self)
		savegame.box_list.append(savegame.income_manpower_box)
		savegame.method_list.append(self.income_manpower)

		savegame.losses_box = Widgets.QCheckBox("Army Losses", self)
		savegame.box_list.append(savegame.losses_box)
		savegame.method_list.append(self.losses)

		savegame.income_stat_box = Widgets.QCheckBox("Income Statistic", self)
		savegame.box_list.append(savegame.income_stat_box)
		savegame.method_list.append(self.income_stat)

		if b:
			savegame.trade_goods_box = Widgets.QCheckBox("Trade Goods", self)
			savegame.box_list.append(savegame.trade_goods_box)
			savegame.method_list.append(self.trade_goods)

		if checks > 0:
			savegame.losses_box.setChecked(True)
		if checks > 1:
			savegame.development_box.setChecked(True)
			savegame.income_manpower_box.setChecked(True)
			savegame.income_stat_box.setChecked(True)
		groupBox = Widgets.QGroupBox(title)
		vbox = Widgets.QVBoxLayout()

		for box in savegame.box_list:
			hbox = Widgets.QHBoxLayout()
			hbox.addWidget(box)
			vbox.addLayout(hbox)
		groupBox.setLayout(vbox)
		return groupBox


	def initUI(self):

		groupBox1 = Widgets.QGroupBox()
		grid1 = Widgets.QGridLayout()
		grid1.addWidget(self.show_button, 0, 0)
		grid1.addWidget(self.close_button, 0, 1)
		grid1.addWidget(self.select_all_button, 1, 0)
		grid1.addWidget(self.deselect_all_button, 1, 1)
		groupBox1.setLayout(grid1)

		groupBox2 = Widgets.QGroupBox()
		grid2 = Widgets.QGridLayout()
		grid2.addWidget(self.army_battle_button, 2, 0)
		grid2.addWidget(self.navy_battle_button, 2, 1)
		grid2.addWidget(self.province_list_button, 3, 0)
		grid2.addWidget(self.wars_button, 3, 1)
		groupBox2.setLayout(grid2)

		groupBox3 = Widgets.QGroupBox()
		grid3 = Widgets.QGridLayout()
		grid3.addWidget(self.overview_button, 0, 0)
		grid3.addWidget(self.total_points_spent_button, 0, 1)
		grid3.addWidget(self.tech_button, 0, 2)
		grid3.addWidget(self.adm_points_spent_button, 1, 0)
		grid3.addWidget(self.dip_points_spent_button, 1, 1)
		grid3.addWidget(self.mil_points_spent_button, 1, 2)
		groupBox3.setLayout(grid3)

		groupBox4 = Widgets.QGroupBox()
		grid4 = Widgets.QGridLayout()
		grid4.addWidget(self.back_button, 0, 0)
		grid4.addWidget(self.upload_button, 0, 1)
		groupBox4.setLayout(grid4)

		vbox = Widgets.QVBoxLayout()
		hbox = Widgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.create_groupbox(self.savegame_list[0], "Savegame 1", 0))
		hbox.addWidget(self.create_groupbox(self.savegame_list[1], "Savegame 2", 1))
		hbox.addWidget(self.create_groupbox(self.savegame_list[2], "Vergleich", 2, False))
		hbox.addStretch(1)
		vbox.addLayout(hbox)

		hbox = Widgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.save_figures_box)
		hbox.addStretch(1)
		vbox.addLayout(hbox)
		vbox.addWidget(groupBox3)
		vbox.addStretch(1)

		hbox = Widgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(groupBox1)
		hbox.addWidget(groupBox2)
		hbox.addStretch(1)
		vbox.addLayout(hbox)
		hbox = Widgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(groupBox4)
		hbox.addStretch(1)
		vbox.addLayout(hbox)

		self.setLayout(vbox)

	def back(self):
		self.back_to_parse_window.emit()

	def upload(self):
		webbrowser.open("https://abload.de/")

	def show_stats(self):
		if self.save_figures_box.isChecked():
			self.openFileNameDialog()
		for savegame in self.savegame_list:
			for box, method in zip(savegame.box_list, savegame.method_list):
				if box.isChecked():
					try:
						method(savegame)
					except Exception as e:
						plt.close("all")
						self.switch_error_window.emit(e)
					box.setChecked(False)
		plt.show()

	def openFileNameDialog(self):
			options = Widgets.QFileDialog.Options()
			options |= Widgets.QFileDialog.DontUseNativeDialog
			fileName = str(Widgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
			if fileName:
				self.directory = fileName

	def select_all(self):
		for savegame in self.savegame_list:
			for box in savegame.box_list:
				box.setChecked(True)

	def deselect_all(self):
		for savegame in self.savegame_list:
			for box in savegame.box_list:
				box.setChecked(False)

	def wars(self):
		d = []
		war_dict_copy = copy.deepcopy(self.savegame_list[1].war_dict)
		for war, losses in war_dict_copy.items():
			entry = losses[-1]
			del entry[1]
			entry[0] = war
			entry.insert(1, losses[1][0])
			entry.insert(1, losses[0][0])
			d.append(entry)
		self.switch_table_window.emit(d, "Wars")

	def army_battle(self):
		self.switch_table_window.emit(self.savegame_list[1].army_battle_list, "Army battles")

	def navy_battle(self):
		self.switch_table_window.emit(self.savegame_list[1].navy_battle_list, "Navy Battles")

	def provinces(self):
		self.switch_table_window.emit(self.savegame_list[1].province_stats_list, "Province Table")

	def development(self, savegame):
		savegame.development_figure = plt.figure("Development - {0}".format(savegame.year))

		ax1 = plt.subplot2grid((5, 2), (0, 0), rowspan=3)
		ax2 = plt.subplot2grid((5, 2), (0, 1), sharey=ax1, rowspan=3)
		ax3 = plt.subplot2grid((5, 2), (4, 0), colspan=3)

		ax1.tick_params(axis='both', which='major', labelsize=8)
		ax2.tick_params(axis='both', which='major', labelsize=8)

		plt.subplots_adjust(hspace = 0.05)
		savegame.development_figure.suptitle(savegame.year, fontsize = 20)
		savegame.development_figure.set_size_inches(16, 8)
		ax1.grid(True, axis="y")
		ax1.minorticks_on()
		ax1.set_title("Development")
		color_list = []

		if savegame == self.savegame_list[2]:
			savegame = self.savegame_list[1]
			compare = True
		else:
			compare = False

		dev_x = [sorted(savegame.stats_dict.items(), key = lambda x: x[1][2], reverse = True)[i][0] for i in range(len(savegame.stats_dict))][:20]
		dev_y = [sorted(savegame.stats_dict.items(), key = lambda x: x[1][2], reverse = True)[i][1][2] for i in range(len(savegame.stats_dict))][:20]
		effective_development_x = [sorted(savegame.stats_dict.items(), key = lambda x: x[1][0], reverse = True)[i][0] for i in range(len(savegame.stats_dict))][:20]
		effective_development_y = [sorted(savegame.stats_dict.items(), key = lambda x: x[1][0], reverse = True)[i][1][0] for i in range(len(savegame.stats_dict))][:20]
		effective_development_table = [sorted(savegame.stats_dict.items(), key = lambda x: x[1][2], reverse = True)[i][1][0] for i in range(len(savegame.stats_dict))][:20]
		if compare:
			base_effective_development_table = self.stats_data_maker(dev_x, self.savegame_list[0].stats_dict, 0)
			base_dev_y = []
			for tag in dev_x:
				if tag in self.formable_nations_dict:
					try:
						base_dev_y.append(savegame.stats_dict[tag][2] - self.savegame_list[0].stats_dict[self.formable_nations_dict[tag]][2])
					except KeyError:
						base_dev_y.append(savegame.stats_dict[tag][2] - self.savegame_list[0].stats_dict[tag][2])
				else:
					base_dev_y.append(savegame.stats_dict[tag][2] - self.savegame_list[0].stats_dict[tag][2])

			norm = plt.Normalize(min(base_dev_y), max(base_dev_y))
			color_list2 = plt.cm.RdYlGn(norm(base_dev_y))



		for tag in dev_x:
			if tag in savegame.color_dict:
				color_list.append(savegame.color_dict[tag])
			else:
				color_list.append("black")
		ax1.bar(range(len(dev_y)), dev_y, label = "Spieltag-Anfang", color = color_list, edgecolor = "grey", linewidth = 1)
		ax1.set_xticks(range(len([sorted(savegame.stats_dict.items(), key = lambda x: x[1][2], reverse = True)[i][1] for i in range(len(savegame.stats_dict))][:20])))
		ax1.set_xticklabels([sorted(savegame.stats_dict.items(), key = lambda x: x[1][2], reverse = True)[i][0] for i in range(len(savegame.stats_dict))][:20])

		if compare:
			ax1.bar(range(len(base_dev_y)), base_dev_y, label = "Spieltag-Ende", color = color_list2, edgecolor = "black", linewidth = 1)

			base_effective_development_y = []
			for tag in effective_development_x:
				try:
					base_effective_development_y.append(savegame.stats_dict[tag][0] - self.savegame_list[0].stats_dict[tag][0])
				except KeyError:
					if tag in self.formable_nations_dict:
						base_effective_development_y.append(savegame.stats_dict[tag][0] - self.savegame_list[0].stats_dict[self.formable_nations_dict[tag]][0])
			norm = plt.Normalize(min(base_effective_development_y), max(base_effective_development_y))
			color_list2 = plt.cm.RdYlGn(norm(base_effective_development_y))

		ax2.grid(True, axis="y")
		ax2.minorticks_on()
		ax2.set_title("Effective Development")
		color_list = []
		for tag in effective_development_x:
			if tag in savegame.color_dict:
				color_list.append(savegame.color_dict[tag])
			else:
				color_list.append("black")
		ax2.bar(range(len(effective_development_y)), effective_development_y, color=color_list, edgecolor = "grey", linewidth = 1)
		ax2.set_xticks(range(len(effective_development_x)))
		ax2.set_xticklabels(effective_development_x)

		if compare:
			ax2.bar(range(len(base_effective_development_y)), base_effective_development_y, label = "Spieltag-Ende", color = color_list2, edgecolor = "black", linewidth = 1)

		colors = []
		cell_text = []
		cell_text.append(["" for x in range(len(dev_y))])
		cell_text.append(dev_y)
		cell_text.append([int(x) for x in effective_development_table])
		if compare:
			cell_text.append(["" for x in range(len(dev_y))])
			cell_text.append(["{0}{1}".format(str([x for x in ["+"] if a > 0])[2:-2], int(a)) for a in base_dev_y])
			cell_text.append(["{0}{1}".format(str([x for x in ["+"] if int(a - b) > 0])[2:-2], int(a - b)) for a,b in zip(effective_development_table, base_effective_development_table)])
			cell_text.append(["" for x in range(len(dev_y))])
			cell_text.append([int(a - b) for a,b in zip(dev_y, base_dev_y)])
			cell_text.append([int(x) for x in base_effective_development_table])
			rows = [savegame.year, "Development", "Effective Development", self.savegame_list[2].year, "Development", "Effective Development", self.savegame_list[0].year, "Development", "Effective Development"]
			row_colors = ["white", "gold", "salmon", "white", "gold", "salmon", "white", "gold", "salmon"]
		else:
			rows = [savegame.year, "Development", "Effective Development"]
			row_colors = ["white", "gold", "salmon"]
		for data in cell_text:
			try:
				clean_data = [float(d) for d in data]
				norm = plt.Normalize(min(clean_data), max(clean_data))
				colors.append(plt.cm.RdYlGn(norm(clean_data)))
			except:
				colors.append(["white" for x in range(len(dev_y))])
		col_colors = []
		for tag in dev_x:
			if tag in savegame.color_dict:
				col_colors.append(savegame.color_dict[tag])
			else:
				col_colors.append("black")
		cols = dev_x


		tab = ax3.table(cellText=cell_text, cellColours=colors, rowLabels=rows, rowColours=row_colors,
						colColours=col_colors, colLabels=cols, loc='center')
		tab.auto_set_font_size(False)
		tab.set_fontsize(10)
		table_props = tab.properties()
		table_cells = table_props['children']
		for cell in table_cells:
			cell.set_height(0.2)
		ax3.axis("Off")

		if self.save_figures_box.isChecked():
			try:
				directory = self.directory
				makedirs(directory)
			except (NameError, AttributeError):
				directory = savegame.directory
				try:
					makedirs (directory)
				except FileExistsError:
					pass
			except FileExistsError:
				pass
			plt.savefig("{0}/development_figure.png".format(directory), dpi=200)

	def stats_data_maker(self, tag_list, data, index):
		stats_list = []
		for tag in tag_list:
			if tag in self.formable_nations_dict:
				try:
					stats_list.append(data[self.formable_nations_dict[tag]][index])
				except KeyError:
					stats_list.append(data[tag][index])
			else:
				stats_list.append(data[tag][index])
		return stats_list

	def income_manpower(self, savegame):
		income_manpower_figure = plt.figure("Income & Manpower - {0}".format(savegame.year))
		compare = False
		ax1 = plt.subplot2grid((5, 2), (0, 0), rowspan=3)
		ax2 = plt.subplot2grid((5, 2), (0, 1), rowspan=3)
		ax3 = plt.subplot2grid((5, 2), (4, 0), colspan=3)
		plt.subplots_adjust(hspace = 0.05)
		income_manpower_figure.set_size_inches(16, 8)
		income_manpower_figure.suptitle(savegame.year, fontsize = 20)
		ax1.grid(True, axis="y")
		ax1.minorticks_on()
		ax1.set_title("Income")
		ax1.set_xlabel("Nation")
		ax1.tick_params(axis='both', which='major', labelsize=8)
		ax2.tick_params(axis='both', which='major', labelsize=8)
		color_list = []

		if savegame == self.savegame_list[2]:
			savegame = self.savegame_list[1]
			compare = True
		income_x = [sorted(savegame.stats_dict.items(), key = lambda x: x[1][4], reverse = True)[i][0] for i in range(len(savegame.stats_dict))]
		income_y = [sorted(savegame.stats_dict.items(), key = lambda x: x[1][4], reverse = True)[i][1][4] for i in range(len(savegame.stats_dict))]
		max_manpower_x = [sorted(savegame.stats_dict.items(), key = lambda x: x[1][6], reverse = True)[i][0] for i in range(len(savegame.stats_dict))]
		max_manpower_y = [sorted(savegame.stats_dict.items(), key = lambda x: x[1][6], reverse = True)[i][1][6] for i in range(len(savegame.stats_dict))]
		max_manpower_table = [sorted(savegame.stats_dict.items(), key = lambda x: x[1][4], reverse = True)[i][1][6] for i in range(len(savegame.stats_dict))]
		for tag in income_x:
			if tag in savegame.color_dict:
				color_list.append(savegame.color_dict[tag])
			else:
				color_list.append("black")
		ax1.bar(range(len(income_y)), income_y, color=color_list, edgecolor = "grey", linewidth = 1)
		ax1.set_xticks(range(len(income_x)))
		ax1.set_xticklabels(income_x)

		if compare:
			base_income_y = []
			for tag in income_x:
				if tag in self.formable_nations_dict:
					try:
						base_income_y.append(savegame.stats_dict[tag][4] - self.savegame_list[0].stats_dict[self.formable_nations_dict[tag]][4])
					except KeyError:
						base_income_y.append(savegame.stats_dict[tag][4] - self.savegame_list[0].stats_dict[tag][4])
				else:
					base_income_y.append(savegame.stats_dict[tag][4] - self.savegame_list[0].stats_dict[tag][4])

			norm = plt.Normalize(min(base_income_y), max(base_income_y))
			color_list2 = plt.cm.RdYlGn(norm(base_income_y))
			ax1.bar(range(len(base_income_y)), base_income_y, color=color_list2, edgecolor = "black", linewidth = 1)


		color_list = []
		for tag in max_manpower_x:
			if tag in savegame.color_dict:
				color_list.append(savegame.color_dict[tag])
			else:
				color_list.append("black")
		ax2.grid(True, axis="y")
		ax2.minorticks_on()
		ax2.set_title("Maximum Manpower")
		ax2.set_xlabel("Nation")
		ax2.bar(range(len(max_manpower_y)), max_manpower_y, color=color_list, edgecolor = "grey", linewidth = 1)
		#ax2.bar(range(len(manpower_y)), manpower_y, color=color_list)
		ax2.set_xticks(range(len(max_manpower_x)))
		ax2.set_xticklabels(max_manpower_x)

		if compare:
			base_max_manpower_y = []
			for tag in max_manpower_x:
				if tag in self.formable_nations_dict:
					try:
						base_max_manpower_y.append(savegame.stats_dict[tag][6] - self.savegame_list[0].stats_dict[self.formable_nations_dict[tag]][6])
					except KeyError:
						base_max_manpower_y.append(savegame.stats_dict[tag][6] - self.savegame_list[0].stats_dict[tag][6])
				else:
					base_max_manpower_y.append(savegame.stats_dict[tag][6] - self.savegame_list[0].stats_dict[tag][6])

			norm = plt.Normalize(min(base_max_manpower_y), max(base_max_manpower_y))
			color_list2 = plt.cm.RdYlGn(norm(base_max_manpower_y))
			ax2.bar(range(len(base_max_manpower_y)), base_max_manpower_y, color=color_list2, edgecolor = "black", linewidth = 1)

			base_max_manpower_table = []
			for tag in income_x:
				if tag in self.formable_nations_dict:
					try:
						base_max_manpower_table.append(self.savegame_list[0].stats_dict[self.formable_nations_dict[tag]][6])
					except KeyError:
						base_max_manpower_table.append(self.savegame_list[0].stats_dict[tag][6])
				else:
					base_max_manpower_table.append(self.savegame_list[0].stats_dict[tag][6])


		cell_text = []
		cell_text.append(["" for x in range(len(income_y))])
		cell_text.append(income_y)
		cell_text.append(['{0:,}'.format(mp) for mp in max_manpower_table])
		if compare:
			cell_text.append(["" for x in range(len(income_y))])
			cell_text.append(["{0}{1}".format(str([x for x in ["+"] if a > 0])[2:-2], int(a*100)/100) for a in base_income_y])
			cell_text.append(["{0}{1:,}".format(str([x for x in ["+"] if int(a - b) > 0])[2:-2], int(a - b)) for a,b in zip(max_manpower_table, base_max_manpower_table)])
			cell_text.append(["" for x in range(len(income_y))])
			cell_text.append([int((a - b)*100)/100 for a,b in zip(income_y, base_income_y)])
			cell_text.append(['{0:,}'.format(int(x)) for x in base_max_manpower_table])
		# formatted = []
		# for manpower in manpower_table:
		#	 formatted.append('{0:,}'.format(manpower))
		# cell_text.append(formatted)
		colors = []
		data_list = []
		data_list.append(["" for x in range(len(income_y))])
		data_list.append(income_y)
		data_list.append(max_manpower_table)
		if compare:
			data_list.append(["" for x in range(len(income_y))])
			data_list.append(base_income_y)
			data_list.append(["{0}{1}".format(str([x for x in ["+"] if int(a - b) > 0])[2:-2], int(a - b)) for a,b in zip(max_manpower_table, base_max_manpower_table)])
			data_list.append(["" for x in range(len(income_y))])
			data_list.append([(a - b) for a,b in zip(income_y, base_income_y)])
			data_list.append([int(x) for x in base_max_manpower_table])
			rows = [savegame.year, "Income", "Maximum Manpower", self.savegame_list[2].year, "Income", "Maximum Manpower", self.savegame_list[0].year, "Income", "Maximum Manpower"] #, "Current Manpower"]
			row_colors = ["white", "gold", "grey", "white", "gold", "grey", "white", "gold", "grey"] #, "dodgerblue"]
		else:
			rows = [savegame.year, "Income", "Maximum Manpower"]
			row_colors = ["white", "gold", "grey"]
		#data_list.append(manpower_table)
		for data in data_list:
			try:
				clean_data = [float(d) for d in data]
				norm = plt.Normalize(min(clean_data), max(clean_data))
				colors.append(plt.cm.RdYlGn(norm(clean_data)))
			except:
				colors.append(["white" for x in range(len(income_y))])
		col_colors = []
		for tag in income_x:
			if tag in savegame.color_dict:
				col_colors.append(savegame.color_dict[tag])
			else:
				col_colors.append("black")
		cols = income_x
		tab = ax3.table(cellText=cell_text, cellColours=colors, rowLabels=rows, rowColours=row_colors,
						colColours=col_colors, colLabels=cols, loc='center')
		tab.auto_set_font_size(False)
		tab.set_fontsize(8)
		table_props = tab.properties()
		table_cells = table_props['children']
		for cell in table_cells:
			cell.set_height(0.2)
		ax3.axis("Off")

		if self.save_figures_box.isChecked():
			try:
				directory = self.directory
				makedirs(directory)
			except (NameError, AttributeError):
				directory = savegame.directory
				try:
					makedirs (directory)
				except FileExistsError:
					pass
			except FileExistsError:
				pass
			plt.savefig("{0}/income_manpower_figure.png".format(directory), dpi=200)

	def income_stat(self, savegame):
		if savegame == self.savegame_list[2]:
			savegame = self.savegame_list[1]
		income_plot = plt.figure("Income-Plot - {0}".format(savegame.year))
		income_plot.suptitle(savegame.year, fontsize = 20)
		income_plot.set_size_inches(10, 8)
		plt.subplots_adjust(right = 0.85)
		a = 0
		color_list = []
		for tag in savegame.playertags:
			if tag in savegame.color_dict:
				color_list.append(savegame.color_dict[tag])
			else:
				color_list.append("black")
		markers = ["o","v","^","<",">","s","p","*","+","x","d","D","h","H"]
		for tag, color in zip(savegame.playertags, color_list):
			marker = markers[a%len(markers)]
			plt.plot(savegame.income_dict[tag][0], savegame.income_dict[tag][1],
					 label=tag, color=color, linewidth=1.5, marker = marker)
			a += 1
		plt.grid(True, which="both")
		plt.minorticks_on()
		max_list = []
		for tag in savegame.playertags:
			max_value = max(savegame.income_dict[tag][1])
			max_list.append(max_value)
		maxi = max(max_list)
		plt.axis([1445, int(savegame.year), 0, maxi * 1.05])
		plt.title("Income Overview")
		xlab = plt.xlabel("Year")
		xlab.set_fontsize(12)
		ylab = plt.ylabel("Yearly Income")
		ylab.set_fontsize(12)
		plt.legend(prop={'size': 11}, loc = (1.04, 0))
		if self.save_figures_box.isChecked():
			try:
				directory = self.directory
				makedirs(directory)
			except (NameError, AttributeError):
				directory = savegame.directory
				try:
					makedirs (directory)
				except FileExistsError:
					pass
			except FileExistsError:
				pass
			plt.savefig("{0}/income_stat_figure.png".format(directory), dpi=800)

	def losses(self, savegame):
		losses_figure = plt.figure("Army Losses - {0}".format(savegame.year))
		losses_figure.suptitle(savegame.year, fontsize = 20)
		year = savegame.year
		compare = False
		losses_figure.suptitle(savegame.year, fontsize = 20)
		ax1 = plt.subplot2grid((3, 2), (0, 0), rowspan=2)
		ax2 = plt.subplot2grid((3, 2), (0, 1), rowspan=2, sharey=ax1)
		ax3 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
		ax1.set_title("Army Losses")
		ax2.set_title("Army Losses")
		ax1.tick_params(axis='both', which='major', labelsize=8)
		ax2.tick_params(axis='both', which='major', labelsize=8)
		cell_text = []
		colors = []
		if savegame == self.savegame_list[2]:
			compare = True
			savegame = self.savegame_list[1]
			base_losses_dict = dict(zip(self.savegame_list[0].sorted_losses_list[0], [[self.savegame_list[0].sorted_losses_list[i][j] for i in range(9)] for j in range(len(self.savegame_list[0].sorted_losses_list[0]))]))
			losses_list = []
			for tag in savegame.sorted_losses_list[0]:
				try:
					losses_list.append([(savegame.sorted_losses_list[i][savegame.sorted_losses_list[0].index(tag)] - base_losses_dict[tag][i] ) for i in range(1,9)])
				except KeyError:
					if tag in self.formable_nations_dict:
						losses_list.append([(savegame.sorted_losses_list[i][savegame.sorted_losses_list[0].index(tag)] - base_losses_dict[self.formable_nations_dict[tag]][i]) for i in range(1,9)])

			losses_list = [savegame.sorted_losses_list[0]]
			for i in range(1,9):
				losses_list.append([])
				for tag in savegame.sorted_losses_list[0]:
					try:
						losses_list[i].append((savegame.sorted_losses_list[i][savegame.sorted_losses_list[0].index(tag)] - base_losses_dict[tag][i]))
					except KeyError:
						losses_list[i].append((savegame.sorted_losses_list[i][savegame.sorted_losses_list[0].index(tag)] - base_losses_dict[self.formable_nations_dict[tag]][i]))
			losses_list[-1] = [int(loss*100)/100 for loss in losses_list[-1]]
			sorted_losses_list = list(zip(*sorted(zip(losses_list[7], losses_list[0], losses_list[1], losses_list[2], losses_list[3], losses_list[4], losses_list[5], losses_list[6], losses_list[8]))))
			sorted_losses_list.insert(7, sorted_losses_list.pop(0))
			sorted_losses_list[-1] = [int(losses/(int(savegame.year) - int(self.savegame_list[0].year))) for losses in sorted_losses_list[-2]]
		ylim = 0
		for i in range(1,9):
			if not compare:
				sorted_losses_list = savegame.sorted_losses_list
			if i != 3:
				if (m := max(sorted_losses_list[i])) > ylim:
					ylim = m
				cell_text.append(['{0:,}'.format(loss) for loss in sorted_losses_list[i]])
				norm = plt.Normalize(min(sorted_losses_list[i]), max(sorted_losses_list[i]))
				colors.append(plt.cm.RdYlGn(norm(sorted_losses_list[i])))
		rows = ["Infantry", "Cavalry", "Artillery", "Combat", "Atrittion", "Total", "Per Year"]
		cols = sorted_losses_list[0]
		row_colors = ["royalblue", "saddlebrown", "k", "indianred", "dimgray", "white", "white"]
		col_colors = []
		for tag in sorted_losses_list[0]:
			col_colors.append(savegame.color_dict[tag])
		tab = ax3.table(cellText=cell_text, cellColours=colors, rowLabels=rows, rowColours=row_colors,
						colColours=col_colors, colLabels=cols, loc='upper center', fontsize=10)
		ax3.axis("Off")
		table_props = tab.properties()
		table_cells = table_props['children']
		x = len(cols) * (len(rows) + 1) + 2
		table_cells[x]._text.set_color("white")
		losses_figure.canvas.set_window_title("Army Losses")
		losses_figure.set_size_inches(16, 10)

		ax1.set_xlabel("Nation")
		ax1.set_ylabel("Number of Soldiers")
		ax1.ticklabel_format(style='plain')
		ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
		ax1.bar(range(len(sorted_losses_list[1])), sorted_losses_list[1],
				label="Infantry", color="royalblue", edgecolor=col_colors, linewidth=1)
		ax1.bar(range(len(sorted_losses_list[2])), sorted_losses_list[2],
				bottom=sorted_losses_list[1], label="Cavalry", color="saddlebrown",
				edgecolor=col_colors, linewidth=1)
		ax1.bar(range(len(sorted_losses_list[4])), sorted_losses_list[4],
				bottom=sorted_losses_list[3], label="Artillery", color="k", edgecolor=col_colors,
				linewidth=1)
		ax1.set_xticks(range(len(sorted_losses_list[0])))
		ax1.set_xticklabels(sorted_losses_list[0])
		ax1.grid(True, axis="y")
		ax1.legend(prop={'size': 10})

		ax2.set_xlabel("Nation")
		ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
		ax2.bar(range(len(sorted_losses_list[5])), sorted_losses_list[5],
				label="Combat", color="indianred", edgecolor=col_colors, linewidth=1)
		ax2.bar(range(len(sorted_losses_list[6])), sorted_losses_list[6],
				bottom=sorted_losses_list[5], label="Atrittion", color="dimgray",
				edgecolor=col_colors, linewidth=1)
		ax2.set_xticks(range(len(sorted_losses_list[0])))
		ax2.set_xticklabels(sorted_losses_list[0])
		print(ylim)
		ax2.set_ylim(0,ylim*1.05)
		ax2.grid(True, axis="y")
		ax2.legend(prop={'size': 10})
		if self.save_figures_box.isChecked():
			try:
				directory = self.directory
				makedirs(directory)
			except (NameError, AttributeError):
				directory = savegame.directory
				try:
					makedirs (directory)
				except FileExistsError:
					pass
			except FileExistsError:
				pass
			plt.savefig("{0}/army_losses_figure_{1}.png".format(directory, year), dpi=200)

	def trade_goods(self, savegame):
		savegame.trade_goods_figure = plt.figure("Trade Goods - {0}".format(savegame.year), figsize=(18, 9))
		ax_list = []
		labels = savegame.datasets[1] + ["Rest"]
		for i in range(1,30):
			ax_list.append(plt.subplot2grid((10,4),((i-1)//4,(i-1)%4)))
			sizes = [good[i] for good in savegame.goods]
			sizes.append(savegame.total_trade_goods[i] - sum(sizes))
			colors = [savegame.color_dict[tag] for tag in labels[:-1]]
			colors.append("grey")
			ax_list[i-1].pie(sizes, colors = colors)
			ax_list[i-1].set_title(trade_goods_list[i])
			plt.subplots_adjust(hspace = 0.3, wspace = 0)

	def overview(self):
		columns = [i for i in range(8)]
		column_count = 9
		header_labels = ["Country", "Effective Development", "Great Power Score", "Development", "Navy Strength", "Income", "Max Manpower", "Total Army Losses", "Total Income over Time"]
		data = self.savegame_list[1].stats_dict
		print(data)
		self.switch_overview_window.emit("Overview Window",columns , column_count, header_labels, data)

	def tech(self):
		columns = [i for i in range(6)]
		column_count = 8
		header_labels = ["Country", "Institution Penalty", "Adm-Tech", "Dip-Tech", "Mil-Tech", "Ideas", "Innovativeness", "Tech Score"]
		data = self.savegame_list[1].tech_dict
		self.switch_overview_window.emit("Tech Window", columns, column_count, header_labels, data)

	def adm_points_spent(self):
		columns = [0,1,2,7,15,17]
		column_count = len(columns)+2
		header_labels = ["Country", "Ideas", "Tech", "Stability","Development", "Reduce Inflation", "Cores", "Total"]
		data = {tag: list(self.savegame_list[1].stats_dict[tag][-1][0].values()) for tag in self.savegame_list[1].playertags}
		self.switch_overview_window.emit("Adm-Points Spent Total", columns, column_count, header_labels, data)

	def dip_points_spent(self):
		columns = [0,1,7,14,20,22,27,34,47]
		column_count = len(columns)+2
		header_labels = ["Country", "Ideas", "Tech","Development", "DipCost Peacedeal", "Culture Conversions", "Reduce War Exhaustion", "Merkantilism", "Promote Culture", "Admirals", "Total"]
		data = {tag: list(self.savegame_list[1].stats_dict[tag][-1][1].values()) for tag in self.savegame_list[1].playertags}
		self.switch_overview_window.emit("Dip-Points Spent Total", columns, column_count, header_labels, data)

	def mil_points_spent(self):
		columns = [0,1,7,21,36,39,46,47]
		column_count = len(columns)+2
		header_labels = ["Country", "Ideas", "Tech", "Development", "Suppress Rebels", "Strengthen Government", "Artillery Barrage", "Force March", "Generals", "Total"]
		data = {tag: list(self.savegame_list[1].stats_dict[tag][-1][2].values()) for tag in self.savegame_list[1].playertags}
		self.switch_overview_window.emit("Mil-Points Spent Total", columns, column_count, header_labels, data)

	def total_points_spent(self):
		columns = [0,1,2]
		column_count = len(columns)+2
		header_labels = ["Country", "Adm", "Dip", "Mil", "Total"]
		data = {tag: list(self.savegame_list[1].stats_dict[tag][-1][3].values()) for tag in self.savegame_list[1].playertags}
		self.switch_overview_window.emit("Total Points Spent", columns, column_count, header_labels, data)

	def close_stats(self):
		plt.close("all")

class MainWindow(Widgets.QMainWindow):
	change_dir = Core.pyqtSignal()

	def __init__(self, savegame_list, formable_nations_dict):
		super().__init__()
		self.main = ShowStats(savegame_list, formable_nations_dict)
		self.setGeometry(0, 30, 640, 480)
		self.setWindowTitle("Decla's Stats-Tool")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.setCentralWidget(self.main)
