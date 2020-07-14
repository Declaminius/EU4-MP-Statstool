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
from math import sqrt
from config import trade_goods_list, icon_dir


class ShowStats(Widgets.QWidget):
	back_to_parse_window = Core.pyqtSignal()
	change_dir = Core.pyqtSignal()
	switch_table_window = Core.pyqtSignal(list, str)
	switch_province_table_window = Core.pyqtSignal(list, str)
	switch_overview_window = Core.pyqtSignal(str, list, list, list, dict)
	switch_monarch_table_window = Core.pyqtSignal(str, list, list)
	switch_error_window = Core.pyqtSignal(str)
	switch_nation_profile = Core.pyqtSignal(str)

	def __init__(self, savegame_list, formable_nations_dict, playertags):
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

		self.monarchs_button = Widgets.QPushButton("Monarchs Table", self)
		self.monarchs_button.released.connect(self.monarchs)

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
		grid3.addWidget(self.monarchs_button, 0, 3)
		grid3.addWidget(self.adm_points_spent_button, 1, 0)
		grid3.addWidget(self.dip_points_spent_button, 1, 1)
		grid3.addWidget(self.mil_points_spent_button, 1, 2)
		groupBox3.setLayout(grid3)

		groupBox4 = Widgets.QGroupBox()
		grid4 = Widgets.QGridLayout()
		grid4.addWidget(self.back_button, 0, 0)
		grid4.addWidget(self.upload_button, 0, 1)
		groupBox4.setLayout(grid4)

		groupBox5 = Widgets.QGroupBox("Nation Profiles")
		grid5 = Widgets.QGridLayout()
		m = int(sqrt(len(self.savegame_list[1].stats_dict.keys())))
		i = 0
		for tag in self.savegame_list[1].stats_dict.keys():
			self.profile_button = Widgets.QPushButton(tag, self)
			self.profile_button.released.connect(self.nation_profiles)
			grid5.addWidget(self.profile_button,i//m,i%m)
			i += 1
		groupBox5.setLayout(grid5)

		vbox = Widgets.QVBoxLayout()
		hbox = Widgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.create_groupbox(self.savegame_list[0], "Savegame 1", 0))
		hbox.addWidget(self.create_groupbox(self.savegame_list[1], "Savegame 2", 1))
		hbox.addWidget(self.create_groupbox(self.savegame_list[2], "Vergleich", 2, False))
		hbox.addWidget(groupBox5)
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
					method(savegame)
					box.setChecked(False)
					# try:
					# 	method(savegame)
					# except Exception as e:
					# 	plt.close("all")
					# 	self.switch_error_window.emit(str(e))
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
		self.switch_table_window.emit(self.savegame_list[1].army_battle_list, "Army Battles")

	def navy_battle(self):
		self.switch_table_window.emit(self.savegame_list[1].navy_battle_list, "Navy Battles")

	def provinces(self):
		self.switch_province_table_window.emit(self.savegame_list[1].province_stats_list, "Province Table")

	def delta(self, category_str, delta_str):
		for tag in self.savegame_list[1].stats_dict.keys():
			if (tag in self.formable_nations_dict.keys()) and \
			(self.formable_nations_dict[tag] in self.savegame_list[0].stats_dict.keys()):
				self.savegame_list[1].stats_dict[tag][delta_str] = self.savegame_list[1].stats_dict[tag][category_str]\
					- self.savegame_list[0].stats_dict[self.formable_nations_dict[tag]][category_str]
			else:
				self.savegame_list[1].stats_dict[tag][delta_str] =  self.savegame_list[1].stats_dict[tag][category_str]\
				- self.savegame_list[0].stats_dict[tag][category_str]
		values = [x for _,x in sorted(zip([self.savegame_list[1].stats_dict[tag][category_str]\
		for tag in self.savegame_list[1].stats_dict.keys()],[self.savegame_list[1].stats_dict[tag][delta_str]\
		for tag in self.savegame_list[1].stats_dict.keys()]), reverse = True)]
		norm = plt.Normalize(min(values), max(values))
		color_list = plt.cm.RdYlGn(norm(values))
		return color_list, values

	def development(self, savegame):
		development_figure = plt.figure("Development - {0}".format(savegame.year))

		ax1 = plt.subplot2grid((5, 2), (0, 0), rowspan=3)
		ax2 = plt.subplot2grid((5, 2), (0, 1), sharey=ax1, rowspan=3)
		ax3 = plt.subplot2grid((5, 2), (4, 0), colspan=3)

		ax1.tick_params(axis='both', which='major', labelsize=8)
		ax2.tick_params(axis='both', which='major', labelsize=8)

		plt.subplots_adjust(hspace = 0.05)
		development_figure.suptitle(savegame.year, fontsize = 20)
		development_figure.set_size_inches(16, 8)
		ax1.grid(True, axis="y")
		ax1.minorticks_on()
		ax1.set_title("Development")
		color_list = []

		if savegame == self.savegame_list[2]:
			savegame = self.savegame_list[1]
			compare = True
		else:
			compare = False

		dev = sorted([(savegame.stats_dict[tag]["development"],tag)\
		for tag in savegame.stats_dict.keys()],key = lambda x: x[0], reverse = True)
		eff_dev = sorted([(savegame.stats_dict[tag]["effective_development"],tag)\
		for tag in savegame.stats_dict.keys()],key = lambda x: x[0], reverse = True)
		eff_dev_table = sorted([(savegame.stats_dict[tag]["effective_development"],\
		savegame.stats_dict[tag]["development"]) for tag in savegame.stats_dict.keys()],\
		key = lambda x: x[1], reverse = True)

		if compare:
			color_list, delta_dev = self.delta("development", "delta_dev")

		for value,tag in dev:
			if tag in savegame.color_dict:
				ax1.bar(tag,value, label = "Spieltag-Anfang",\
				color = savegame.color_dict[tag], edgecolor = "grey", linewidth = 1)
			else:
				ax1.bar(tag,value, label = "Spieltag-Anfang",\
				color = "black", edgecolor = "grey", linewidth = 1)

		if compare:
			ax1.bar(range(len(delta_dev)), delta_dev, label = "Spieltag-Ende", color = color_list, edgecolor = "black", linewidth = 1)

			color_list, delta_eff_dev_plot = self.delta("effective_development", "delta_eff_dev")
			delta_eff_dev_table = [x for _,x in sorted(zip([savegame.stats_dict[tag]["development"]\
			for tag in savegame.stats_dict.keys()],[savegame.stats_dict[tag]["delta_eff_dev"]\
			for tag in savegame.stats_dict.keys()]), reverse = True)]

		ax2.grid(True, axis="y")
		ax2.minorticks_on()
		ax2.set_title("Effective Development")
		for value,tag in eff_dev:
			if tag in savegame.color_dict:
				ax2.bar(tag,value, color = savegame.color_dict[tag], edgecolor = "grey", linewidth = 1)
			else:
				ax2.bar(tag,value, color = "black", edgecolor = "grey", linewidth = 1)

		if compare:
			ax2.bar(range(len(delta_eff_dev_plot)), delta_eff_dev_plot, label = "Spieltag-Ende", color = color_list, edgecolor = "black", linewidth = 1)

		colors = []
		cell_text = []
		cell_text.append(["" for x in dev])
		cell_text.append([int(value) for value,tag in dev])
		cell_text.append([int(x[0]) for x in eff_dev_table])
		if compare:
			cell_text.append(["" for x in dev])
			cell_text.append(["+{}".format(int(a)) if a > 0 else str(int(a)) for a in delta_dev])
			cell_text.append(["+{}".format(int(a)) if a > 0 else str(int(a)) for a in delta_eff_dev_table])
			cell_text.append(["" for x in dev])
			cell_text.append([int(a[0] - b) for a,b in zip(dev, delta_dev)])
			cell_text.append([int(a[0] - b) for a,b in zip(eff_dev_table, delta_eff_dev_table)])
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
				colors.append(["white" for x in dev])
		col_colors = []
		for value,tag in dev:
			if tag in savegame.color_dict:
				col_colors.append(savegame.color_dict[tag])
			else:
				col_colors.append("black")
		cols = [x[1] for x in dev]


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

		if savegame == self.savegame_list[2]:
			savegame = self.savegame_list[1]
			compare = True

		income = sorted([(savegame.stats_dict[tag]["income"],tag)\
		for tag in savegame.stats_dict.keys()],key = lambda x: x[0], reverse = True)

		max_manpower = sorted([(savegame.stats_dict[tag]["max_manpower"],tag)\
		for tag in savegame.stats_dict.keys()],key = lambda x: x[0], reverse = True)

		max_manpower_table = [x for _,x in sorted([(savegame.stats_dict[tag]["income"],\
		savegame.stats_dict[tag]["max_manpower"]) for tag in savegame.stats_dict.keys()], reverse = True)]

		for value,tag in income:
			if tag in savegame.color_dict:
				ax1.bar(tag, value, color = savegame.color_dict[tag], edgecolor = "grey", linewidth = 1)
			else:
				ax1.bar(tag, value, color = "black", edgecolor = "grey", linewidth = 1)

		if compare:
			color_list, delta_income = self.delta("income", "delta_income")
			ax1.bar(range(len(delta_income)), delta_income, color=color_list,\
			edgecolor = "black", linewidth = 1)

		for value,tag in max_manpower:
			if tag in savegame.color_dict:
				ax2.bar(tag, value, color=savegame.color_dict[tag],\
				edgecolor = "grey", linewidth = 1)
			else:
				ax2.bar(tag, value, "black", edgecolor = "grey", linewidth = 1)
		ax2.grid(True, axis="y")
		ax2.minorticks_on()
		ax2.set_title("Maximum Manpower")
		ax2.set_xlabel("Nation")

		if compare:
			color_list, delta_max_manpower = self.delta("max_manpower", "delta_max_manpower")

			delta_max_manpower_table = [x for _,x in sorted(zip([savegame.stats_dict[tag]["income"]\
			for tag in savegame.stats_dict.keys()],[savegame.stats_dict[tag]["delta_max_manpower"]\
			for tag in savegame.stats_dict.keys()]), reverse = True)]

			ax2.bar(range(len(delta_max_manpower)), delta_max_manpower, color=color_list, edgecolor = "black", linewidth = 1)

		cell_text = []
		cell_text.append(["" for x in income])
		cell_text.append([str(value) for value,tag in income])
		cell_text.append(['{0:,}'.format(mp) for mp in max_manpower_table])
		if compare:
			cell_text.append(["" for x in income])
			cell_text.append(["+{}".format(int(a*100)/100) if a > 0 else str(int(a*100)/100)\
			for a in delta_income])
			cell_text.append(["+{0:,}".format(int(a)) if a > 0 else "{0:,}".format(int(a))\
			for a in delta_max_manpower_table])
			cell_text.append(["" for x in income])
			cell_text.append([str(int((a[0] - b)*100)/100) for a,b in zip(income, delta_income)])
			cell_text.append(['{0:,}'.format(int(a-b))\
			for a,b in zip(max_manpower_table,delta_max_manpower_table)])
			rows = [savegame.year, "Income", "Maximum Manpower", self.savegame_list[2].year, "Income", "Maximum Manpower", self.savegame_list[0].year, "Income", "Maximum Manpower"] #, "Current Manpower"]
			row_colors = ["white", "gold", "grey", "white", "gold", "grey", "white", "gold", "grey"] #, "dodgerblue"]
		else:
			rows = [savegame.year, "Income", "Maximum Manpower"]
			row_colors = ["white", "gold", "grey"]
		colors = []
		for data in cell_text:
			try:
				clean_data = [float(d.replace(",","")) for d in data]
				norm = plt.Normalize(min(clean_data), max(clean_data))
				colors.append(plt.cm.RdYlGn(norm(clean_data)))
			except:
				colors.append(["white" for x in income])
		col_colors = []
		for value, tag in income:
			if tag in savegame.color_dict:
				col_colors.append(savegame.color_dict[tag])
			else:
				col_colors.append("black")
		cols = [tag for value,tag in income]
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
			income_plot = plt.figure("Income-Plot - {0}".format(savegame.year))
			income_plot.suptitle(savegame.year, fontsize = 20)
			savegame = self.savegame_list[1]
			compare = True
		else:
			income_plot = plt.figure("Income-Plot - {0}".format(savegame.year))
			income_plot.suptitle(savegame.year, fontsize = 20)
			compare = False

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
			if tag in savegame.income_dict.keys():
				if compare and (year := int(self.savegame_list[0].year)) in savegame.income_dict[tag][0]:
					i = savegame.income_dict[tag][0].index(year)
					plt.plot(savegame.income_dict[tag][0][i:], savegame.income_dict[tag][1][i:],
							 label=tag, color=color, linewidth=1.5, marker = marker)
				else:
					plt.plot(savegame.income_dict[tag][0], savegame.income_dict[tag][1],
						 label=tag, color=color, linewidth=1.5, marker = marker)
			a += 1
		plt.grid(True, which="both")
		plt.minorticks_on()
		maxi = 0
		for tag in savegame.playertags:
			if tag in savegame.income_dict.keys():
				max_value = max(savegame.income_dict[tag][1])
				if max_value > maxi:
					maxi = max_value
		if compare:
			plt.axis([int(self.savegame_list[0].year), int(savegame.year), 0, maxi * 1.05])
		else:
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
			if compare:
				plt.savefig("{0}/income_stat_figure_compare.png".format(directory), dpi=800)
			else:
				plt.savefig("{0}/income_stat_figure.png".format(directory), dpi=800)

	def losses(self, savegame):
		title = savegame.year
		losses_figure = plt.figure("Army Losses - {0}".format(title))
		losses_figure.suptitle(title, fontsize = 20)
		losses_figure.canvas.set_window_title("Army Losses")
		losses_figure.set_size_inches(16, 10)
		if savegame == self.savegame_list[2]:
			savegame = self.savegame_list[1]
			compare = True
			years = int(self.savegame_list[1].year) - int(self.savegame_list[0].year)
		else:
			compare = False
			years = int(savegame.year) - 1444
		ax1 = plt.subplot2grid((3, 2), (0, 0), rowspan=2)
		ax2 = plt.subplot2grid((3, 2), (0, 1), rowspan=2, sharey=ax1)
		ax3 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
		ax1.set_title("Army Losses")
		ax2.set_title("Army Losses")
		ax1.tick_params(axis='both', which='major', labelsize=8)
		ax2.tick_params(axis='both', which='major', labelsize=8)
		infantry = [x for _,x in sorted([(sum(savegame.stats_dict[tag]["losses"]),\
		savegame.stats_dict[tag]["losses"][0] +\
		savegame.stats_dict[tag]["losses"][1]) for tag in savegame.stats_dict.keys()], reverse = True)]

		cavalry = [x for _,x in sorted([(sum(savegame.stats_dict[tag]["losses"]),\
		savegame.stats_dict[tag]["losses"][3] +\
		savegame.stats_dict[tag]["losses"][4]) for tag in savegame.stats_dict.keys()], reverse = True)]

		artillery = [x for _,x in sorted([(sum(savegame.stats_dict[tag]["losses"]),\
		savegame.stats_dict[tag]["losses"][6] +\
		savegame.stats_dict[tag]["losses"][7]) for tag in savegame.stats_dict.keys()], reverse = True)]

		combat = [x for _,x in sorted([(sum(savegame.stats_dict[tag]["losses"]),\
		savegame.stats_dict[tag]["losses"][0] +\
		savegame.stats_dict[tag]["losses"][3] +\
		savegame.stats_dict[tag]["losses"][6]) for tag in savegame.stats_dict.keys()], reverse = True)]

		attrition = [x for _,x in sorted([(sum(savegame.stats_dict[tag]["losses"]),\
		savegame.stats_dict[tag]["losses"][1] +\
		savegame.stats_dict[tag]["losses"][4] +\
		savegame.stats_dict[tag]["losses"][7]) for tag in savegame.stats_dict.keys()], reverse = True)]

		total = sorted([sum(savegame.stats_dict[tag]["losses"]) for tag in savegame.stats_dict.keys()], reverse = True)
		per_year = [int(x/years) for x in total]

		tags = [x for _,x in sorted([(sum(savegame.stats_dict[tag]["losses"]),tag)\
		for tag in savegame.stats_dict.keys()], reverse = True)]

		if compare:
			total_tags = [(total[tags.index(tag)] - sum(self.savegame_list[0].stats_dict[tag]["losses"]),tag)\
			for tag in tags if tag in self.savegame_list[0].stats_dict.keys()]
			for tag in savegame.stats_dict.keys():
				if tag not in self.savegame_list[0].stats_dict.keys():
					if self.formable_nations_dict[tag] in self.savegame_list[0].stats_dict.keys():
						total_tags.append((sum(savegame.stats_dict[tag]["losses"]) -\
						sum(self.savegame_list[0].stats_dict[self.formable_nations_dict[tag]]["losses"]),tag))
			total, tags = [list(x) for x in zip(*sorted(total_tags, reverse = True))]
			per_year = [int(x/years) for x in total]
			tags = [[tag,tag] if tag in self.savegame_list[0].stats_dict.keys() else [tag,self.formable_nations_dict[tag]] for tag in tags]
			new_tags = [tag[0] for tag in tags]

			infantry = [savegame.stats_dict[tag[0]]["losses"][0] +\
			savegame.stats_dict[tag[0]]["losses"][1] -
			(self.savegame_list[0].stats_dict[tag[1]]["losses"][0] +\
			self.savegame_list[0].stats_dict[tag[1]]["losses"][1]) for tag in tags]

			cavalry = [savegame.stats_dict[tag[0]]["losses"][3] +\
			savegame.stats_dict[tag[0]]["losses"][4] -
			(self.savegame_list[0].stats_dict[tag[1]]["losses"][3] +\
			self.savegame_list[0].stats_dict[tag[1]]["losses"][4]) for tag in tags]

			artillery = [savegame.stats_dict[tag[0]]["losses"][6] +\
			savegame.stats_dict[tag[0]]["losses"][7] -
			(self.savegame_list[0].stats_dict[tag[1]]["losses"][6] +\
			self.savegame_list[0].stats_dict[tag[1]]["losses"][7]) for tag in tags]

			combat = [savegame.stats_dict[tag[0]]["losses"][0] +\
			savegame.stats_dict[tag[0]]["losses"][3] +\
			savegame.stats_dict[tag[0]]["losses"][6] -\
			(self.savegame_list[0].stats_dict[tag[1]]["losses"][0] +\
			self.savegame_list[0].stats_dict[tag[1]]["losses"][3] +\
			self.savegame_list[0].stats_dict[tag[1]]["losses"][6]) for tag in tags]

			attrition = [savegame.stats_dict[tag[0]]["losses"][1] +\
			savegame.stats_dict[tag[0]]["losses"][4] +\
			savegame.stats_dict[tag[0]]["losses"][7] -\
			(self.savegame_list[0].stats_dict[tag[1]]["losses"][1] +\
			self.savegame_list[0].stats_dict[tag[1]]["losses"][4] +\
			self.savegame_list[0].stats_dict[tag[1]]["losses"][7]) for tag in tags]

		if not compare:
			new_tags = tags
		col_colors = []
		for tag in new_tags:
			col_colors.append(savegame.color_dict[tag])
		ylim = max(total)

		ax1.set_xlabel("Nation")
		ax1.set_ylabel("Number of Soldiers")
		ax1.ticklabel_format(style='plain')
		ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
		ax1.bar(new_tags, infantry, label="Infantry", color="royalblue",
				edgecolor=col_colors, linewidth=1)
		ax1.bar(new_tags, cavalry, bottom=infantry, label="Cavalry", color="saddlebrown",
				edgecolor=col_colors, linewidth=1)
		ax1.bar(new_tags, artillery, bottom=[x+y for x,y in zip(infantry,cavalry)],
				label="Artillery", color="k", edgecolor=col_colors, linewidth=1)
		ax1.grid(True, axis="y")
		ax1.legend(prop={'size': 10})

		ax2.set_xlabel("Nation")
		ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
		ax2.bar(new_tags, combat,
				label="Combat", color="indianred", edgecolor=col_colors, linewidth=1)
		ax2.bar(new_tags, attrition, bottom=combat, label="Atrittion",
				color="dimgray", edgecolor=col_colors, linewidth=1)
		ax2.set_ylim(0,ylim*1.05)
		ax2.grid(True, axis="y")
		ax2.legend(prop={'size': 10})

		cell_text = []
		colors = []
		for row in [infantry,cavalry,artillery,combat,attrition,total,per_year]:
			cell_text.append(['{0:,}'.format(loss) for loss in row])
			norm = plt.Normalize(min(row), max(row))
			colors.append(plt.cm.RdYlGn(norm(row)))
		rows = ["Infantry", "Cavalry", "Artillery", "Combat", "Atrittion", "Total", "Per Year"]
		cols = new_tags
		row_colors = ["royalblue", "saddlebrown", "k", "indianred", "dimgray", "white", "white"]
		tab = ax3.table(cellText=cell_text, cellColours=colors, rowLabels=rows, rowColours=row_colors,
						colColours=col_colors, colLabels=cols, loc='upper center', fontsize=10)
		ax3.axis("Off")
		table_props = tab.properties()
		table_cells = table_props['children']
		x = len(cols) * (len(rows) + 1) + 2
		table_cells[x]._text.set_color("white")
		for cell in table_cells:
			cell.set_height(0.15)

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
			plt.savefig("{0}/army_losses_figure_{1}.png".format(directory, title), dpi=200)

	def trade_goods(self, savegame):
		trade_goods_figure = plt.figure("Trade Goods - {0}".format(savegame.year), figsize=(18, 9))
		ax_list = []
		for i in range(1,30):
			ax_list.append(plt.subplot2grid((10,4),((i-1)//4,(i-1)%4)))
			sizes = [savegame.stats_dict[tag]["trade_goods"][i] for tag in savegame.stats_dict.keys()]
			sizes.append(savegame.total_trade_goods[i] - sum(sizes))
			colors = [savegame.color_dict[tag] for tag in savegame.stats_dict.keys()]
			colors.append("grey")
			ax_list[i-1].pie(sizes, colors = colors)
			ax_list[i-1].set_title(trade_goods_list[i])
			plt.subplots_adjust(hspace = 0.3, wspace = 0)

	def overview(self):
		header_labels = ["Country", "Effective Development", "Great Power Score", "Development",\
		"Navy Strength", "Income", "Max Manpower", "Total Army Losses", "Total Income over Time"]
		categories = ["effective_development","great_power_score","development","navy_strength",\
		"income","max_manpower","total_losses","total_income"]
		data = self.savegame_list[1].stats_dict
		colormap_options = [0] + [0]*len(categories)
		self.switch_overview_window.emit("Overview Window", categories, colormap_options, header_labels, data)

	def tech(self):
		header_labels = ["Country", "Institution Penalty", "Adm-Tech", "Dip-Tech",\
		"Mil-Tech", "Ideas", "Innovativeness", "Tech Score"]
		categories = ["institution_penalty","adm","dip","mil","number_of_ideas","innovativeness","tech_score"]
		data = self.savegame_list[1].tech_dict
		colormap_options = [0] + [2] + [0]*(len(categories) - 1)
		self.switch_overview_window.emit("Tech Window", categories, colormap_options, header_labels, data)

	def monarchs(self):
		header_labels = ["Country", "Name", "Adm", "Dip", "Mil", "Total Pips"]
		data = self.savegame_list[1].monarch_list
		self.switch_monarch_table_window.emit("Monarch Table", data, header_labels)

	def adm_points_spent(self):
		header_labels = ["Country", "Ideas", "Tech", "Stability","Development",\
		"Reduce Inflation", "Cores", "Total"]

		categories = [0,1,2,7,15,17,-1]
		colormap_options = [0] + [0]*len(categories)
		data = {tag: list(self.savegame_list[1].stats_dict[tag]["points_spent"][0].values())\
		+ [self.savegame_list[1].stats_dict[tag]["points_spent"][3]["adm"]]\
		for tag in self.savegame_list[1].stats_dict.keys()}
		self.switch_overview_window.emit("Adm-Points Spent Total", categories,\
		colormap_options, header_labels, data)

	def dip_points_spent(self):
		header_labels = ["Country", "Ideas", "Tech","Development", "DipCost Peacedeal",\
		"Culture Conversions", "Reduce War Exhaustion", "Merkantilism",\
		"Promote Culture", "Admirals", "Total"]

		categories = [0,1,7,14,20,22,27,34,47,-1]
		colormap_options = [0] + [0]*len(categories)
		data = {tag: list(self.savegame_list[1].stats_dict[tag]["points_spent"][1].values())\
		+ [self.savegame_list[1].stats_dict[tag]["points_spent"][3]["dip"]]\
		for tag in self.savegame_list[1].stats_dict.keys()}
		self.switch_overview_window.emit("Dip-Points Spent Total", categories,\
		colormap_options, header_labels, data)

	def mil_points_spent(self):
		header_labels = ["Country", "Ideas", "Tech", "Development",\
		"Suppress Rebels", "Strengthen Government", "Artillery Barrage",\
		"Force March", "Generals", "Total"]

		categories = [0,1,7,21,36,39,45,46,-1]
		colormap_options = [0] + [0]*len(categories)
		data = {tag: list(self.savegame_list[1].stats_dict[tag]["points_spent"][2].values())\
		+ [self.savegame_list[1].stats_dict[tag]["points_spent"][3]["mil"]]\
		for tag in self.savegame_list[1].stats_dict.keys()}
		self.switch_overview_window.emit("Mil-Points Spent Total", categories,\
		colormap_options, header_labels, data)

	def total_points_spent(self):
		header_labels = ["Country", "Adm", "Dip", "Mil", "Tech", "Ideas", "Development", "Total"]
		categories = ["adm","dip","mil","tech","ideas","dev","total"]
		colormap_options = [0,0,0,0,0,0,0,0]
		data = {tag: self.savegame_list[1].stats_dict[tag]["points_spent"][3]\
		for tag in self.savegame_list[1].stats_dict.keys()}
		self.switch_overview_window.emit("Total Points Spent", categories,\
		colormap_options, header_labels, data)

	def nation_profiles(self):
		tag = self.sender().text()
		self.switch_nation_profile.emit(tag)

	def close_stats(self):
		plt.close("all")

class MainWindow(Widgets.QMainWindow):
	change_dir = Core.pyqtSignal()

	def __init__(self, savegame_list, formable_nations_dict, playertags):
		super().__init__()
		self.main = ShowStats(savegame_list, formable_nations_dict, playertags)
		self.setGeometry(0, 30, 640, 480)
		self.setWindowTitle("Decla's Stats-Tool")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.setCentralWidget(self.main)
