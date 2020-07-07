# -*- coding: windows-1252 -*-
"""
Created on Wed Dec 25 02:52:26 2019

@author: Florian
"""

class Savegame():
	def __init__(self, playertags =  None, tag_list = None, savefile = None):
		self.playertags = playertags
		self.tag_list = tag_list
		self.file = savefile