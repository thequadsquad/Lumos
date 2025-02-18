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
        

class CCs_AHA_Diff_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'Statistical AHA Difference Figure'
        
    def make_tab(self, gui, view, evals1, evals2):
        self.gui  = gui
        self.view = view
        self.evals1 = evals1
        self.evals2 = evals2
        gui.tabs.addTab(self, "Statistical AHA Diff: "+str(evals1[0].name))
        layout = self.layout
        layout = QGridLayout(gui)
        layout.setSpacing(7)
        
        try:
            self.figure = Statistical_T1_diff_bullseye_plot()
            self.canvas = FigureCanvas(self.figure)
            self.figure.set_values(view, evals1, evals2, self.canvas)
            self.figure.visualize()
            self.canvas.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
            self.canvas.setFocus()
            self.toolbar = NavigationToolbar(self.canvas, gui)
            layout.addWidget(self.canvas,   0, 0, 1,1)
            layout.addWidget(self.toolbar,  1, 0, 1,1)
            
        except Exception as e:
            print(traceback.format_exc())
        
        self.setLayout(layout)

        
            