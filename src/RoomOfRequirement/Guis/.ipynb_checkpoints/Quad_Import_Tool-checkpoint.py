import os
from pathlib import Path
import sys
import traceback

from PyQt6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QApplication, QLabel, QStatusBar, QStyle, QCheckBox, QGridLayout, QPushButton, QLineEdit, QFrame#, QAction
from PyQt6.QtGui import QIcon, QColor, QPalette, QAction
from PyQt6.QtCore import Qt, QSize

import qdarktheme

from RoomOfRequirement.Quad import QUAD_Manager
from RoomOfRequirement.Guis.Quad_Manager_Tabs.centralintroductory_tab  import CentralIntroductory_TabWidget
from RoomOfRequirement.Guis.Quad_Manager_Tabs.cohortviewer_tab         import CohortViewer_TabWidget
from RoomOfRequirement.Guis.Quad_Manager_Tabs.imageimport_tab          import Imageimport_TabWidget
from RoomOfRequirement.Guis.Quad_Manager_Tabs.annotationimport_tab     import Annotationimport_TabWidget
from RoomOfRequirement.Guis.Quad_Manager_Tabs.export_tab               import Export_TabWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Room of Requirement - QUAD Import")
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
        introduction_action = QAction(QIcon(os.path.join(self.bp, 'Icons','notebook.png')),   "&Introduction", self)
        introduction_action.setStatusTip("General information about this tool.")
        introduction_action.triggered.connect(self.open_introduction_tab)
        
        cohortviewer_action = QAction(QIcon(os.path.join(self.bp, 'Icons','wand--arrow.png')), "&Cohort Viewer", self)
        cohortviewer_action.setStatusTip("Design or View Cohorts.")
        cohortviewer_action.triggered.connect(self.open_cohortviewer_tab)
        
        imageimport_action = QAction(QIcon(os.path.join(self.bp, 'Icons','wand--arrow.png')), "&Image Import", self)
        imageimport_action.setStatusTip("Import Images.")
        imageimport_action.triggered.connect(self.open_imageimport_tab)
        
        annoimport_action = QAction(QIcon(os.path.join(self.bp, 'Icons','wand--arrow.png')),  "&Annotation Import", self)
        annoimport_action.setStatusTip("Import Annotations.")
        annoimport_action.triggered.connect(self.open_annotationimport_tab)
        
        export_action = QAction(QIcon(os.path.join(self.bp, 'Icons','wand--arrow.png')),  "&Export Functions", self)
        export_action.setStatusTip("Export Functions.")
        export_action.triggered.connect(self.open_export_tab)
        
        
        # MENU BAR
        menu = self.menuBar()
        file_menu = menu.addMenu("&Select Tools")
        file_menu.addAction(introduction_action)
        file_menu.addAction(cohortviewer_action)
        file_menu.addAction(imageimport_action)
        file_menu.addAction(annoimport_action)
        file_menu.addAction(export_action)
        
        # Central Tab - is replaced with other tabs as selected
        self.tab = CentralIntroductory_TabWidget(self)
        self.setCentralWidget(self.tab)

        # Set Statusbar for information display during use / mouse hovering
        self.setStatusBar(QStatusBar(self))

    def open_introduction_tab(self, s):
        self.tab = CentralIntroductory_TabWidget(self)
        self.setCentralWidget(self.tab)

    def open_cohortviewer_tab(self, s):
        self.tab = CohortViewer_TabWidget(self, self.quad)
        self.setCentralWidget(self.tab)
        
    def open_imageimport_tab(self, s):
        self.tab = Imageimport_TabWidget(self, self.quad)
        self.setCentralWidget(self.tab)
        
    def open_annotationimport_tab(self, s):
        self.tab = Annotationimport_TabWidget(self, self.quad)
        self.setCentralWidget(self.tab)

    def open_export_tab(self, s):
        self.tab = Export_TabWidget(self, self.quad)
        self.setCentralWidget(self.tab)
        
        
        
def main():
    app = QApplication(sys.argv)
    
    # Now use a palette to switch to dark colors:
    #app.setStyle("Fusion")
    #palette = QPalette()
    #palette.setColor(QPalette.Window, QColor(53, 53, 53))
    #palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    """
    palette.setColor(QPalette.window, QColor(53, 53, 53))
    palette.setColor(QPalette.windowText, QColor(255, 255, 255))
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