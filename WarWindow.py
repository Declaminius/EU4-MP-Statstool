# -*- coding: windows-1252 -*-
"""
Created on Wed Dec 25 02:50:59 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
from config import icon_dir

class WarWindow(Widgets.QWidget):
	def __init__(self):
		super().__init__()
		self.initMe()

	def initMe(self):
		self.setGeometry(0, 30, 1920, 800)
		self.setWindowTitle("War Overview")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.button_list = []
		vbox = Widgets.QVBoxLayout()
		scroll = Widgets.QScrollArea()
		vbox.addWidget(scroll)
		scroll.setWidgetResizable(True)
		scroll_content = Widgets.QWidget(scroll)
		scroll_layout = Widgets.QGridLayout(scroll_content)
		scroll_content.setLayout(scroll_layout)
		real_war_list = [war for war in window.savegame_list[1].war_list if war in [war[-1] for war in window.savegame_list[1].army_battle_list]]
		i = 0
		for war in real_war_list:
			i += 1
			war_button = Widgets.QPushButton(war, self)
			war_button.released.connect(self.build_table)
			self.button_list.append(war_button)
			scroll_layout.addWidget(war_button, i%10,int(i/10))
		scroll.setWidget(scroll_content)

		self.setLayout(vbox)
		self.show()

	def build_table(self):
		sender = self.sender()
		war = sender.text()
		new_data = window.savegame_list[1].war_dict[war]
		self.war_table = TableWindow(new_data, war)
