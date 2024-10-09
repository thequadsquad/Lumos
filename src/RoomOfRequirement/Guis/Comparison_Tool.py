import os
from pathlib import Path
import sys
import traceback

from PyQt6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QApplication, QLabel, QStatusBar, QStyle, QCheckBox, QGridLayout, QPushButton, QLineEdit, QFrame
from PyQt6.QtGui import QIcon, QColor, QPalette, QAction
from PyQt6.QtCore import Qt, QSize

import qdarktheme

from RoomOfRequirement.Guis.Comparison_Tabs.database_tab import Database_TabWidget
from RoomOfRequirement.Guis.Comparison_Tabs.CCs_Overview_Tab import CCs_Overview_Tab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Battle of Hogwarts - Reader Comparison")
        shift       = 30
        self.left   = 0
        self.top    = shift
        self.width  = 1200
        self.height = 800  + shift
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        self.bp = Path(__file__).parent.absolute()
        self.ui_init()
        
    def ui_init(self):
        # Central Tab - is replaced with other tabs as selected
        self.tab = Database_TabWidget(self)
        self.setCentralWidget(self.tab)

        # Set Statusbar for information display during use / mouse hovering
        self.setStatusBar(QStatusBar(self))
        
    def add_ccs_overview_tab(self, quad, cases1, cases2):
        tab = CCs_Overview_Tab(self.tab, quad, cases1, cases2)
        
        
def main():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
    

if __name__ == '__main__':
    main()