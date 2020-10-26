# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:30:42 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from config import icon_dir

class ConfigureNationFormations(Widgets.QWidget):
	set_nation_formations = Core.pyqtSignal(dict)

	def __init__(self, savegame_list, old_nations_list, new_nations_list, formable_nations_dict):
		super().__init__()
		self.old_nations_list = old_nations_list
		self.new_nations_list = new_nations_list
		self.formable_nations_dict = formable_nations_dict
		self.setGeometry(0, 30, 400, 100)
		self.setWindowTitle("Configure Nation Formations")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.arrow_label = Widgets.QLabel(chr(10230), self)
		arrow_font = Gui.QFont("Times", 16)
		self.old_label = Widgets.QLabel("Old Nation", self)
		self.new_label = Widgets.QLabel("New Nation", self)
		self.arrow_label.setFont(arrow_font)
		self.configure_nation1 = Widgets.QComboBox(self)
		self.configure_nation2 = Widgets.QComboBox(self)
		for tag in savegame_list[0].tag_list:
			self.configure_nation1.addItem(tag)
		for tag in savegame_list[1].tag_list:
			self.configure_nation2.addItem(tag)
		self.confirm_button = Widgets.QPushButton("Add Combination", self)
		self.confirm_button.released.connect(self.add_combination)
		self.delete_button = Widgets.QPushButton("Delete All", self)
		self.delete_button.released.connect(self.delete)
		self.standard_button = Widgets.QPushButton("Reset to Standard", self)
		self.standard_button.released.connect(self.standard)
		self.close_button = Widgets.QPushButton("Close", self)
		self.close_button.released.connect(self.close)
		self.initUI()

	def initUI(self):
		vbox = Widgets.QVBoxLayout()
		hbox = Widgets.QHBoxLayout()
		hbox.addWidget(self.old_label)
		hbox.addStretch(1)
		hbox.addWidget(self.new_label)
		vbox.addLayout(hbox)
		hbox = Widgets.QHBoxLayout()
		hbox.addWidget(self.configure_nation1)
		hbox.addStretch(1)
		hbox.addWidget(self.arrow_label)
		hbox.addStretch(1)
		hbox.addWidget(self.configure_nation2)
		vbox.addLayout(hbox)
		vbox.addStretch(1)
		hbox = Widgets.QHBoxLayout()
		hbox.addWidget(self.confirm_button)
		hbox.addWidget(self.delete_button)
		hbox.addWidget(self.standard_button)
		vbox.addLayout(hbox)
		vbox.addWidget(self.close_button)
		self.setLayout(vbox)

	def add_combination(self):
		self.formable_nations_dict[self.configure_nation2.currentText()] = self.configure_nation1.currentText()
		self.set_nation_formations.emit(self.formable_nations_dict)

	def delete(self):
		self.formable_nations_dict = {}
		self.set_nation_formations.emit(self.formable_nations_dict)

	def standard(self):
		self.set_nation_formations.emit(dict(zip(self.new_nations_list, self.old_nations_list)))
