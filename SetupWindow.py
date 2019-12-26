# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:14:51 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from parserfunctions import edit_parse
from Savegame import Savegame

icon_dir = "files/attack_move.png"

class SetupWindow(Widgets.QMainWindow):
	switch_window = Core.pyqtSignal()
	
	def __init__(self):
		super().__init__()
		self.savegame_list = [[],[]]
		self.status = self.statusBar()
		self.line1 = Widgets.QLineEdit()
		self.line1.setReadOnly(True)
		self.line1.setMinimumSize(350, 22)
		self.line2 = Widgets.QLineEdit()
		self.line2.setReadOnly(True)
		self.line2.setMinimumSize(350, 22)
		self.select_button1 = Widgets.QPushButton("Savegame 1", self)
		self.select_button2 = Widgets.QPushButton("Savegame 2", self)
		self.select_data_button1 = Widgets.QPushButton("Select Data 1", self)
		self.select_data_button2 = Widgets.QPushButton("Select Data 2", self)
		self.select_data_button1.setEnabled(False)
		self.select_data_button2.setEnabled(False)
		self.parse_button = Widgets.QPushButton("Parse")
		self.init_ui()

	def init_ui(self):
		self.setGeometry(760,490,400,100)
		self.setWindowTitle("Decla's Stats-Tool")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.select_button1.released.connect(self.get_playertags)
		self.select_data_button1.released.connect(self.get_data)
		self.select_button2.released.connect(self.get_playertags)
		self.select_data_button2.released.connect(self.get_data)
		self.parse_button.released.connect(self.parse)
		group_box = Widgets.QGroupBox()
		vbox = Widgets.QVBoxLayout()
		hbox = Widgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.line1)
		hbox.addWidget(self.select_button1)
		hbox.addWidget(self.select_data_button1)
		hbox.addStretch(1)
		vbox.addLayout(hbox)
		hbox = Widgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.line2)
		hbox.addWidget(self.select_button2)
		hbox.addWidget(self.select_data_button2)
		hbox.addStretch(1)
		vbox.addLayout(hbox)
		vbox.addStretch(1)
		vbox.addWidget(self.parse_button)
		group_box.setLayout(vbox)
		self.setCentralWidget(group_box)

	def get_playertags(self):
		sender = self.sender()
		self.openFileNameDialog()
		try:
			self.playertags, self.tag_list = edit_parse(self.FILEDIR)
			self.FILENAME = self.FILEDIR.split("/")[-1]
			if sender.text() == "Savegame 1":
				self.line1.setText(self.FILEDIR)
			if sender.text() == "Savegame 2":
				self.line2.setText(self.FILEDIR)
			self.status.showMessage("")
		except AttributeError:
			pass
		except (IndexError, UnicodeDecodeError):
			self.status.showMessage("{} is not a EU4-Savegame".format(self.FILEDIR))
		try:
			savegame = Savegame(self.playertags, self.tag_list, self.FILEDIR)
			savegame.directory = "C:/Users/kunde/Desktop/{}-images".format(self.FILENAME.split(".")[0])
			savegame.data_flag = False
			if sender.text() == "Savegame 1":
				self.savegame_list[0] = savegame
			if sender.text() == "Savegame 2":
				self.savegame_list[1] = savegame
		except (NameError, AttributeError):
			pass

	def get_data(self):
		sender = self.sender()
		self.openFileNameDialog()
		try:
			global nations_names_dict, tag_list
			with open (self.FILEDIR) as savefile:
				content = savefile.read()
				try:
					nations_names_dict, tag_list, _ = eval(content)
				except:
					self.status.showMessage("Wrong file")
			self.nations_names_dict = nations_names_dict
			self.FILENAME = self.FILEDIR.split("/")[-1]
			if sender.text() == "Select Data 1":
				self.line1.setText(self.FILEDIR)
			if sender.text() == "Select Data 2":
				self.line2.setText(self.FILEDIR)
			self.status.showMessage("")
		except AttributeError:
			pass
		except (IndexError, UnicodeDecodeError):
			self.status.showMessage("Wrong file")
		try:
			savegame = Savegame(nations_names_dict, tag_list, self.FILEDIR)
			savegame.directory = "C:/Users/kunde/Desktop/{}-images".format(self.FILENAME.split(".")[0])
			savegame.data_flag = False
			self.savegame_list.append(savegame)
		except NameError:
			pass

	def openFileNameDialog(self):
		options = Widgets.QFileDialog.Options()
		fileName, _ = Widgets.QFileDialog.getOpenFileName(self, "Select Savegame", "", "All Files (*);;Python Files (*.py)",
												  options=options)
		if fileName:
			self.FILEDIR = fileName

	def parse(self):
		self.switch_window.emit()