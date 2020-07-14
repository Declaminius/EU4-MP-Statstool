# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 02:47:44 2019

@author: Florian
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from config import icon_dir


class ProfileWindow(Widgets.QWidget):

	def __init__(self, tag, loc):
		super().__init__()
		self.setGeometry(0, 30, 600, 100)
		self.setWindowTitle("Nation Profile: {}".format(loc[tag]))
		self.setWindowIcon(Gui.QIcon(icon_dir))
		self.show()
