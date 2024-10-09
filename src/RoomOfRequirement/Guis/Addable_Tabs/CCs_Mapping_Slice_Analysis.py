from PyQt6.QtWidgets import QMainWindow, QGridLayout, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QTextEdit, QTableView, QTableWidgetItem, QComboBox, QHeaderView, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QDialog, QRadioButton, QButtonGroup, QInputDialog
from PyQt6.QtGui import QIcon, QColor
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

import copy

import pandas as pd

from RoomOfRequirement.loading_functions import *
from RoomOfRequirement.Tables import *
from RoomOfRequirement.Figures import *


class CCs_MappingSliceAnalysis_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'Mapping Slice Analysis'
        
    def make_tab(self, gui, view, evals1, evals2):
        self.gui = gui
        gui.tabs.addTab(self, "Mapping Slice Analysis")
        layout = self.layout
        layout = QGridLayout(gui)
        layout.setSpacing(7)
        
        self.fig1    = Mapping_ReferencePointAngleDiff_Boxplot()
        self.canvas1 = FigureCanvas(self.fig1)
        self.fig1.set_canvas(self.canvas1); self.fig1.set_gui(gui)
        self.canvas1.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.canvas1.setFocus()
        self.toolbar1 = NavigationToolbar(self.canvas1, gui)
        try: self.fig1.visualize(view, evals1, evals2)
        except: print(traceback.format_exc())
        layout.addWidget(self.canvas1,  2,0, 1,1)
        layout.addWidget(self.toolbar1, 3,0, 1,1)
        
        self.fig2    = Mapping_ReferencePointDistance_Boxplot()
        self.canvas2 = FigureCanvas(self.fig2)
        self.fig2.set_canvas(self.canvas2); self.fig2.set_gui(gui)
        self.canvas2.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.canvas2.setFocus()
        self.toolbar2 = NavigationToolbar(self.canvas2, gui)
        try: self.fig2.visualize(view, evals1, evals2)
        except: print(traceback.format_exc())
        layout.addWidget(self.canvas2,  2,1, 1,1)
        layout.addWidget(self.toolbar2, 3,1, 1,1)
        
        self.fig3 = Mapping_Slice_Average_PairedBoxplot()
        self.canvas3 = FigureCanvas(self.fig3)
        self.fig3.set_canvas(self.canvas3); self.fig3.set_gui(gui)
        self.canvas3.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.canvas3.setFocus()
        self.toolbar3 = NavigationToolbar(self.canvas3, gui)
        try: self.fig3.visualize(view, evals1, evals2)
        except: print(traceback.format_exc())
        layout.addWidget(self.canvas3,  4,0, 1,1)
        layout.addWidget(self.toolbar3, 5,0, 1,1)
        
        self.fig4 = Mapping_DiceBySlice()
        self.canvas4 = FigureCanvas(self.fig4)
        self.fig4.set_canvas(self.canvas4); self.fig4.set_gui(gui)
        self.canvas4.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.canvas4.setFocus()
        self.toolbar4 = NavigationToolbar(self.canvas4, gui)
        try: self.fig4.visualize(view, evals1, evals2)
        except: print(traceback.format_exc())
        layout.addWidget(self.canvas4,  4,1, 1,1)
        layout.addWidget(self.toolbar4, 5,1, 1,1)
        
        #layout.setRowStretch(0, 3)
        self.setLayout(layout)
        