# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:36:07 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
from config import icon_dir

class ErrorWindow(Widgets.QWidget):
	def __init__(self, error_string):
		super().__init__()
		self.setGeometry(0, 30, 200, 100)
		self.setWindowTitle("Error Window")
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.error_label = Widgets.QLabel("Something went wrong.\nError: \n{0}".format(error_string), self)
		hbox = Widgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.error_label)
		hbox.addStretch(1)
		self.setLayout(hbox)
