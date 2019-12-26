# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:49:35 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from parserfunctions import colormap
icon_dir = "files/attack_move.png"

class Overview(Widgets.QWidget):
	def __init__(self, savegame_list, title, columns, column_count, header_labels, data, censored = [], censored_loc = []):
		super().__init__()
		self.savegame_list = savegame_list
		self.columns = columns
		self.column_count = column_count
		self.data = data
		self.censored = censored
		self.setGeometry(0, 30, 1920, 800)
		self.setWindowTitle(title)
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.first_box = Widgets.QGroupBox(self)
		vbox = Widgets.QVBoxLayout()
		self.table = Widgets.QTableWidget()
		self.table.setColumnCount(column_count)
		self.table.setRowCount(len(self.savegame_list[1].stats_dict))
		self.table.setSortingEnabled(True)
		self.table.setHorizontalHeaderLabels(header_labels)

		color_list = []
		total_list = []
		for x, tag in zip(range(len(self.savegame_list[1].stats_dict.keys())),self.savegame_list[1].stats_dict.keys()):
			item = Widgets.QTableWidgetItem()
			item.setData(Core.Qt.DisplayRole, tag)
			self.table.setItem(x, 0, item)
			if tag in self.savegame_list[1].color_dict:
				self.table.item(x, 0).setBackground(Gui.QColor(self.savegame_list[1].color_dict[self.table.item(x, 0).text()]))
		for x in columns:
			if data == self.savegame_list[1].tech_dict and x == 0:
				color = colormap([data[tag][x] for tag in self.savegame_list[1].stats_dict.keys() if tag not in censored], 2, 255) # Institution penalty should be color-mapped in reverse
			else:
				color = colormap([data[tag][x] for tag in self.savegame_list[1].stats_dict.keys() if tag not in censored], 0, 255)
			for x in censored_loc:
				color.insert(x, (255,255,255))
			color_list.append(color)
		for tag in self.savegame_list[1].stats_dict.keys():
			if tag not in censored:
				if data == self.savegame_list[1].tech_dict:
					total_list.append(sum([data[tag][z] for z in columns[1:-1]])*(1+data[tag][5]/100)/data[tag][0])
				else:
					total_list.append(sum([data[tag][z] for z in columns]))
			else:
				total_list.append("ZENSIERT")

		if data == self.savegame_list[1].stats_dict:
			total_losses_list = []
			self.overview(color_list, total_losses_list)

		else:
			color = colormap([x for x in total_list if x != "ZENSIERT"], 0, 255)
			for x in censored_loc:
				color.insert(x, (255,255,255))
			color_list.append(color)
			for tag, x in zip(self.savegame_list[1].stats_dict.keys(), range(len(self.savegame_list[1].stats_dict.keys()))):
				if tag not in censored:
					y = 1
					for z in columns:
						item = Widgets.QTableWidgetItem()
						item.setData(Core.Qt.DisplayRole, data[tag][z])
						self.table.setItem(x, y, item)
						y += 1
					item = Widgets.QTableWidgetItem()
					item.setData(Core.Qt.DisplayRole, total_list[x])
					self.table.setItem(x, column_count-1, item)
				else:
					y = 1
					for z in columns:
						item = Widgets.QTableWidgetItem()
						item.setData(Core.Qt.DisplayRole, "ZENSIERT")
						self.table.setItem(x, y, item)
						y += 1
					item = Widgets.QTableWidgetItem()
					item.setData(Core.Qt.DisplayRole, total_list[x])
					self.table.setItem(x, column_count-1, item)
			for color, x in zip(color_list, range(len(color_list))):
				for c, y in zip(color, range(len(color))):
					try:
						self.table.item(y, x+1).setBackground(Gui.QColor(*c))
					except:
						print(y,x+1)

		self.table.resizeColumnsToContents()

		vbox.addWidget(self.table)

		self.first_box.setLayout(vbox)

		vbox = Widgets.QHBoxLayout()
		vbox.addWidget(self.first_box)
		self.setLayout(vbox)

		self.show()

	def overview(self, color_list, total_losses_list):
		del (color_list[-2])
		for tag, x in zip(self.savegame_list[1].stats_dict.keys(), range(len(self.savegame_list[1].stats_dict.keys()))):
			y = 1
			for z in range(self.column_count-1):
				if z !=  5:
					item = Widgets.QTableWidgetItem()
					item.setData(Core.Qt.DisplayRole, self.data[tag][z])
					self.table.setItem(x, y, item)
					y += 1
			l = self.data[tag][7]
			total_losses = (l[0] + l[1] + l[3] + l[4] + l[6] + l[7])
			total_losses_list.append(total_losses)
			item = Widgets.QTableWidgetItem()
			item.setData(Core.Qt.DisplayRole, total_losses)
			self.table.setItem(x, 7, item)

		color = colormap(total_losses_list, 0, 255)
		for x, c in zip(range(len(self.savegame_list[1].stats_dict.keys())), color):
			self.table.item(x, 7).setBackground(Gui.QColor(*c))

		for color, x in zip(color_list, range(len(color_list))):
			for c, y in zip(color, range(len(color))):
				self.table.item(y, x+1).setBackground(Gui.QColor(*c))