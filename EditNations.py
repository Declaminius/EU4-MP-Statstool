# -*- coding: windows-1252 -*-
"""
Created on Wed Dec 25 02:32:09 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from config import icon_dir

class EditNations(Widgets.QWidget):
	set_playertags = Core.pyqtSignal()

	def __init__(self, b, playertags, tag_list):
		super().__init__()
		self.b = b
		self.tag_list = tag_list
		self.playertags = playertags
		self.initMe()

	def initMe(self):
		if self.b:
			label_text = "Add Nation"
		else:
			label_text = "Remove Nation"
		self.setGeometry(0, 30, 400, 100)
		self.setWindowTitle(label_text)
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.choose_nation = Widgets.QComboBox(self)
		if self.b:
			self.choose_nation.addItem("")
			for tag in self.tag_list:
				if not tag in self.playertags:
					self.choose_nation.addItem(tag)
		else:
			for tag in self.playertags:
				self.choose_nation.addItem(tag)
		self.confirm_button = Widgets.QPushButton("Confirm", self)
		self.close_button = Widgets.QPushButton("Close", self)
		vbox = Widgets.QVBoxLayout()
		hbox = Widgets.QHBoxLayout()
		hbox.addWidget(self.choose_nation)
		vbox.addLayout(hbox)
		vbox.addStretch(1)
		hbox = Widgets.QHBoxLayout()
		hbox.addWidget(self.confirm_button)
		hbox.addWidget(self.close_button)
		vbox.addLayout(hbox)
		self.setLayout(vbox)
		self.confirm_button.released.connect(self.change_nation)
		self.close_button.released.connect(self.close)

	def change_nation(self):
		text = self.choose_nation.currentText()
		index = self.choose_nation.currentIndex()
		if self.b:
			if text:
				if text not in self.playertags:
					self.playertags.append(text)
					self.playertags.sort()
		else:
			self.playertags.remove(text)
			self.choose_nation.removeItem(index)
		self.set_playertags.emit()
