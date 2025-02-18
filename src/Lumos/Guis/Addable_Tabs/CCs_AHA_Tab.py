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

from Lumos.loading_functions import *
from Lumos.Tables import *
from Lumos.Figures import *
        

class CCs_AHA_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'Stats AHA Figure'
        
    def make_tab(self, gui, view, evals1, evals2):
        self.gui  = gui
        self.view = view
        self.evals1 = evals1
        self.evals2 = evals2
        gui.tabs.addTab(self, "Stats Cases AHA: "+str(evals1[0].name))
        layout = self.layout
        layout = QGridLayout(gui)
        layout.setSpacing(7)
        
        try:
            self.readerchoice_combobox = QComboBox()
            self.readerchoice_combobox.addItems(['Select Reader', 'R1', 'R2'])
            self.readerchoice_combobox.activated.connect(self.update)
            layout.addWidget(self.readerchoice_combobox, 0,0, 1,1)
        
            self.figure = Statistical_T1_bullseye_plot()
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
                self.figure.set_values(self.view, self.evals1, self.canvas)
                self.figure.visualize()
            if reader=='R2':
                self.figure.set_values(self.view, self.evals2, self.canvas)
                self.figure.visualize()
        except Exception as e:
            print(traceback.format_exc())
        
            