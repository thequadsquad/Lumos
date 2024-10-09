from PyQt6.QtWidgets import QMainWindow, QGridLayout, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QTextEdit, QTableView, QTableWidgetItem, QComboBox, QHeaderView, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QDialog, QRadioButton, QButtonGroup, QInputDialog
from PyQt6.QtGui import QIcon, QColor
#from PyQt6.Qt import Qt
from PyQt6 import QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from pathlib import Path
import pickle
import copy
import sys
import os
import inspect
import traceback

import pandas

from RoomOfRequirement.loading_functions import *
from RoomOfRequirement.Tables import *
from RoomOfRequirement.Figures import *
        

class CC_AHA_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'AHA Figure'
        
    def make_tab(self, gui, view, eval1, eval2):
        self.gui   = gui
        self.view  = view
        self.eval1 = eval1
        self.eval2 = eval2
        gui.tabs.addTab(self, "Case AHA: "+str(eval1.name))
        layout = self.layout
        layout = QGridLayout(gui)
        layout.setSpacing(7)
        
        try:
            
            self.readerchoice_combobox = QComboBox()
            self.readerchoice_combobox.addItems(['Select Reader', 'R1', 'R2'])
            self.readerchoice_combobox.activated.connect(self.update)
            layout.addWidget(self.readerchoice_combobox, 0,0, 1,1)
        
            self.figure = T1_bullseye_plot()
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
            self.canvas.setFocus()
            self.toolbar = NavigationToolbar(self.canvas, gui)
            layout.addWidget(self.canvas,   0, 1, 10,2)
            layout.addWidget(self.toolbar, 11, 1,  1,2)
            
        except Exception as e:
            print(traceback.format_exc())
        
        self.setLayout(layout)

        
    def update(self):
        try:
            reader = self.readerchoice_combobox.currentText()
            if reader=='Select Reader': return
            if reader=='R1':
                self.figure.set_values(self.view, self.eval1, self.canvas)
                self.figure.visualize()
            if reader=='R2':
                self.figure.set_values(self.view, self.eval2, self.canvas)
                self.figure.visualize()
            self.canvas.setFocusPolicy(Qt.Qt.ClickFocus)
            self.canvas.setFocus()
        except Exception as e:
            print(traceback.format_exc())
        
            