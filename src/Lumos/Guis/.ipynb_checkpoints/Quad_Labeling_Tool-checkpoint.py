import os
from pathlib import Path
import sys
import traceback

from PyQt6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QApplication, QLabel, QStatusBar, QStyle, QCheckBox, QGridLayout, QPushButton, QLineEdit, QFrame#, qApp
from PyQt6.QtGui import QIcon, QColor, QPalette, QAction
from PyQt6.QtCore import Qt, QSize

import qdarktheme

from RoomOfRequirement.Quad import QUAD_Manager
from RoomOfRequirement.Guis.Quad_Manager_Tabs.centralintroductory_tab  import CentralIntroductory_TabWidget
from RoomOfRequirement.Guis.Quad_Manager_Tabs.imagelabeling_tab        import ImageLabeling_1_TabWidget
from RoomOfRequirement.Guis.Quad_Manager_Tabs.imagelabeling_tab_2      import ImageLabeling_2_TabWidget
from RoomOfRequirement.Guis.Quad_Manager_Tabs.casesimport_tab          import Casesimport_TabWidget
from RoomOfRequirement.Guis.Quad_Manager_Tabs.caselabeling_tab         import CaseLabeling_TabWidget



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Room of Requirement - QUAD Labeling")
        shift       = 30
        self.left   = 0
        self.top    = shift
        self.width  = 1200
        self.height = 800  + shift
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        self.bp = Path(__file__).parent.absolute()
        self.quad = QUAD_Manager()
        self.ui_init()
        
    def ui_init(self):
        introduction_action = QAction(QIcon(os.path.join(self.bp, 'Icons','notebook.png')),    "&Introduction", self)
        introduction_action.setStatusTip("General information about this tool.")
        introduction_action.triggered.connect(self.open_introduction_tab)
        
        labeler_action = QAction(QIcon(os.path.join(self.bp, 'Icons','tag--pencil.png')),      "&Manual Image Labeling", self)
        labeler_action.setStatusTip("Identify and label images.")
        labeler_action.triggered.connect(self.add_imagetagging_tab)
        
        casesimport_action = QAction(QIcon(os.path.join(self.bp, 'Icons','wand--arrow.png')),  "&Cases Import", self)
        casesimport_action.setStatusTip("Import Cases.")
        casesimport_action.triggered.connect(self.open_casesimport_tab)
        
        caselabeling_action = QAction(QIcon(os.path.join(self.bp, 'Icons','wand--arrow.png')), "&Manual Case Labeling", self)
        caselabeling_action.setStatusTip("Label Cases.")
        caselabeling_action.triggered.connect(self.open_caselabeling_tab)
        
        
        
        # MENU BAR
        menu = self.menuBar()
        file_menu = menu.addMenu("&Select Tools")
        file_menu.addAction(introduction_action)
        file_menu.addAction(labeler_action)
        file_menu.addAction(casesimport_action)
        file_menu.addAction(caselabeling_action)
        
        # Central Tab - is replaced with other tabs as selected
        self.tab = CentralIntroductory_TabWidget(self)
        self.setCentralWidget(self.tab)

        # Set Statusbar for information display during use / mouse hovering
        self.setStatusBar(QStatusBar(self))

    def open_introduction_tab(self, s):
        self.tab = CentralIntroductory_TabWidget(self)
        self.setCentralWidget(self.tab)
        
    def open_casesimport_tab(self, s):
        self.tab = Casesimport_TabWidget(self, self.quad)
        self.setCentralWidget(self.tab)

    def add_imagetagging_tab(self, s):
        self.tab = ImageLabeling_1_TabWidget(self, self.quad)
        self.setCentralWidget(self.tab)
        
    def add_singleimagetagging_tab(self, quad, sops, old_lltags, annos_dict):
        t = ImageLabeling_2_TabWidget(self, quad, sops, old_lltags, annos_dict)
        self.tab.tabs.addTab(t, 'Manual Precise Tagging Tab')
        
    def open_caselabeling_tab(self, s):
        self.tab = CaseLabeling_TabWidget(self, self.quad)
        self.setCentralWidget(self.tab)
        
        
        
def main():
    app = QApplication(sys.argv)
    
    # Now use a palette to switch to dark colors:
    """
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(0,0,0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0,0,0))
    app.setPalette(palette)
    """
    
    #qdarktheme.setup_theme()
    
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
    

if __name__ == '__main__':
    main()