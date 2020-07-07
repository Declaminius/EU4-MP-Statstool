# -*- coding: windows-1252 -*-
"""
Created on Wed Dec 25 02:48:40 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from config import icon_dir

class ProvinceFilter(Widgets.QWidget):
	update_table = Core.pyqtSignal(str, list)

	def __init__(self, index, data):
		super().__init__()
		self.data = data
		self.index = index
		self.setGeometry(0, 30, 600, 100)
		self.setWindowTitle("Select")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.select_filter = Widgets.QComboBox(self)
		filter_list = sorted(set([province[index] for province in self.data]))
		for f in filter_list:
			self.select_filter.addItem(f)
		self.select_filter.move(100,40)
		self.select_filter.activated[str].connect(self.filter)
		self.show()

	def filter(self, x):
		self.close()
		new_data = [province for province in self.data if province[self.index] == x]
		self.update_table.emit("province", new_data)
