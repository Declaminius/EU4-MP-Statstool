# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:32:09 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
icon_dir = "files/attack_move.png"

class EditNations(Widgets.QWidget):
	set_playertags = Core.pyqtSignal()

	def __init__(self, b, savegame_list):
		super().__init__()
		self.b = b
		self.savegame_list = savegame_list
		self.initMe()

	def initMe(self):
		if self.b:
			label_text = "Add Nation"
			self.label1 = Widgets.QLabel("Savegame 1", self)
			self.label2 = Widgets.QLabel("Savegame 2", self)
			self.choose_nation2 = Widgets.QComboBox(self)
		else:
			label_text = "Remove Nation"
		self.setGeometry(0, 30, 400, 100)
		self.setWindowTitle(label_text)
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.choose_nation1 = Widgets.QComboBox(self)
		if self.b:
			for savegame, combo in zip(self.savegame_list, (self.choose_nation1, self.choose_nation2)):
				combo.addItem("")
				for tag in savegame.tag_list:
					if not tag in savegame.playertags:
						combo.addItem(tag)
		else:
			for tag in (self.savegame_list[1].tag_list):
				if tag in (set(self.savegame_list[0].playertags + self.savegame_list[1].playertags)):
					self.choose_nation1.addItem(tag)
		self.confirm_button = Widgets.QPushButton("Confirm", self)
		self.close_button = Widgets.QPushButton("Close", self)
		vbox = Widgets.QVBoxLayout()
		if self.b:
			hbox = Widgets.QHBoxLayout()
			hbox.addWidget(self.label1)
			hbox.addWidget(self.label2)
			vbox.addLayout(hbox)
		hbox = Widgets.QHBoxLayout()
		hbox.addWidget(self.choose_nation1)
		if self.b:
			hbox.addWidget(self.choose_nation2)
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
		if self.b:
			for i,text in zip(range(2),[self.choose_nation1.currentText(), self.choose_nation2.currentText()]):
				if text and text not in self.savegame_list[i].playertags:
					self.savegame_list[i].playertags.append(text)
		else:
			if self.choose_nation1.currentText() in self.savegame_list[0].playertags:
				self.savegame_list[0].playertags.remove(self.choose_nation1.currentText())
			if self.choose_nation1.currentText() in self.savegame_list[1].playertags:
				self.savegame_list[1].playertags.remove(self.choose_nation1.currentText())
			self.choose_nation1.removeItem(self.choose_nation1.currentIndex())
		self.set_playertags.emit()
