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
	def __init__(self, savegame_list, playertags, title, categories, colormap_options, header_labels, data):
		super().__init__()
		self.savegame_list = savegame_list
		self.playertags = playertags
		self.data = data
		self.categories = categories
		self.colormap_options = colormap_options
		self.setGeometry(0, 30, 1920, 800)
		self.setWindowTitle(title)
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.first_box = Widgets.QGroupBox(self)
		vbox = Widgets.QVBoxLayout()
		self.table = Widgets.QTableWidget()
		self.table.setColumnCount(len(header_labels))
		self.table.setRowCount(len(self.savegame_list[1].stats_dict))
		self.table.setSortingEnabled(True)
		self.table.setHorizontalHeaderLabels(header_labels)

		self.color_list = []
		total_list = []

		# Inserting nation tags
		i = 0
		for tag in self.playertags:
			item = Widgets.QTableWidgetItem()
			item.setData(Core.Qt.DisplayRole, tag)
			self.table.setItem(i, 0, item)
			if tag in self.savegame_list[1].color_dict:
				self.table.item(i, 0).setBackground\
				(Gui.QColor(self.savegame_list[1].color_dict[self.table.item(i, 0).text()]))
			i += 1

		self.overview()

		self.table.resizeColumnsToContents()

		vbox.addWidget(self.table)

		self.first_box.setLayout(vbox)

		vbox = Widgets.QHBoxLayout()
		vbox.addWidget(self.first_box)
		self.setLayout(vbox)

		self.show()

	def overview(self):
		y = 1
		for category in self.categories:
			x = 0
			color = colormap([self.data[tag][category] for tag in self.playertags],\
			self.colormap_options[y - 1], 255)
			for tag in self.playertags:
				item = Widgets.QTableWidgetItem()
				item.setData(Core.Qt.DisplayRole, self.data[tag][category])
				self.table.setItem(x, y, item)
				self.table.item(x,y).setBackground(Gui.QColor(*color[x]))
				x += 1
			y += 1
