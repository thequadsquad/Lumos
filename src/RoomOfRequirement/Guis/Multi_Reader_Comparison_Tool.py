import os
from pathlib import Path
import sys
import traceback

from PyQt6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QApplication, QLabel, QStatusBar, QStyle, QCheckBox, QGridLayout, QPushButton, QLineEdit, QFrame
from PyQt6.QtGui import QIcon, QColor, QPalette, QAction
from PyQt6.QtCore import Qt, QSize

import qdarktheme

from RoomOfRequirement.Guis.Multi_Comparison_Tabs.multi_database_tab import Multi_Database_TabWidget
from RoomOfRequirement.Guis.Multi_Comparison_Tabs.CCs_Multi_Overview_Tab import CCs_Multi_Overview_Tab

from RoomOfRequirement.Guis.Addable_Tabs import *

###################################################
## executable file - opens central selection tab ##
###################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lumos - Multi Reader Comparison")
        shift       = 30
        self.left   = 0
        self.top    = shift
        self.width  = 1500
        self.height = 800  + shift
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        self.bp = Path(__file__).parent.absolute()
        self.ui_init()
        
    def ui_init(self):
        # Central Selection Tab - is replaced with other tabs as selected
        self.tab = Multi_Database_TabWidget(self)
        self.setCentralWidget(self.tab)

        # Set Statusbar for information display during use / mouse hovering
        self.setStatusBar(QStatusBar(self))
        
    def add_ccs_overview_tab(self, quad, cases_list):
        tab = CCs_Multi_Overview_Tab(self.tab, quad, cases_list)
        
        
def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
    

if __name__ == '__main__':
    main()