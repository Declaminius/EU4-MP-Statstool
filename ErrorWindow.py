# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:36:07 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
icon_dir = "files/attack_move.png"

class ErrorWindow(Widgets.QWidget):
	def __init__(self, text):
		super().__init__()
		self.setGeometry(0, 30, 200, 100)		
		self.setWindowTitle("Error Window")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.error_label = Widgets.QLabel(text, self)
		hbox = Widgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.error_label)
		hbox.addStretch(1)
		self.setLayout(hbox)
		self.show()
