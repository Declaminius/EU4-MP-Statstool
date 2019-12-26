# Author: Florian Schager
# Version: 2.0.
# Last edited: 25.12.2019

"""
Changelog 2.0.:
	> Code Cleanup
	> Splitting the code into multiple files
	> Commenting some functions
	> Replaced from x import * with import x
	> Removed feature, where you could doubleclick the name of any war in war window to get individual war stats,
	  because I used currentWidgets, which seems to be undefined in every imported module.

	> Runtime Optimization of parse-Function:
	> Benchmark Savegames: Spieltag01 & Spieltag02 from Staatsbankrott ist auch keine Lösung
	> Starting time: 3.53 - 3.56 & 3.85 - 3.86 sec

	> Current: 2.83 - 2.86 & 3.16 - 3.19 sec (obsolete figures)
	> Time Saved (absolute): 0.47 - 0.53 & 0.66 - 0.70 sec
	> Time Saved (percentage): 18,98% - 20,51% & 17,14% - 18,13%


	> Fixed bug in tech window showing higher institution penalties as green instead of red
	> Fixed bug in province window caused by provinces with no religion or culture
	> Fixed bug in province window caused by missing = in paradox files
	> Fixed bug in province window caused by unnecessary double province_ids in paradox area file
	> Updated province list to 1.29

	> Changed standard nation formations to fit current MP
	> Added Innovatiness to Tech Window
	> Changed Calculation of Tech Score to: (Number of Techs + Number of Ideas)*(1+Innovatiness/100)/(Institution Penalty)

"""


### Projects ###
# Nation Profiles
# Code Commenting & Cleanup
# Dynamic Censoring
# HRE - Stuff:
# BIP
# HRE-Army & Manpower
# Add default checks to checkboxes

# Better Color-Coding
# Thicker Plot Lines
# Add relative change

import sys
import PyQt5.QtWidgets as Widgets
from Controller import Controller


def main():
	Widgets.QApplication.setStyle(Widgets.QStyleFactory.create("Fusion"))
	app = Widgets.QApplication(sys.argv)
	window = Controller()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
