# Author: Florian Schager
# Version: 2.1.
# Last edited: 27.06.2020

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

Changelog 2.0.1.:

	> Error Window functional again
	> Added default checks to Stats-Navigation-Checkboxes
	> Filtered out battles with less than 10.000 men or less than 10 ships
	> Slight design changes
	> Changed the colormap

Changelog 2.1.:

	> Compatability with 1.30
	> Fixed remove nation bug
	> Made Income-Stat-Plot more readable
	> Major Code Restructuring
	> Code Readability Improvements
	> Added Total Income over Time to Overview Window
"""


### Projects ###
# Nation Profiles
# Code Commenting & Cleanup

# Thicker Plot Lines
# Add relative change

import sys
import PyQt5.QtWidgets as Widgets
from Controller import Controller


def main():
	Widgets.QApplication.setStyle(Widgets.QStyleFactory.create("Fusion"))
	app = Widgets.QApplication(sys.argv)
	app.lastWindowClosed.connect(app.quit)
	window = Controller()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
