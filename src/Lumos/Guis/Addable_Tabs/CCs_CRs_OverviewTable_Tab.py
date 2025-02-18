from PyQt6.QtWidgets import QMainWindow, QGridLayout, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QTextEdit, QTableView, QTableWidgetItem, QComboBox, QHeaderView, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QDialog, QRadioButton, QButtonGroup, QInputDialog
from PyQt6.QtGui import QIcon, QColor
from PyQt6 import QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt

from pathlib import Path
import pickle
import copy
import sys
import os
import inspect
import traceback

import pandas

from Lumos.Views   import *
from Lumos.loading_functions import *
from Lumos.Tables  import *
from Lumos.Figures import *


class CCs_CRs_OverviewTable_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'CCs_CRs_OverviewTable_Tab'
        
    def make_tab(self, gui, view, evals1, evals2):
        self.gui  = gui
        self.view = view
        self.evals1, self.evals2 = evals1, evals2
        gui.tabs.addTab(self, "Overview Table")
        layout = self.layout
        layout = QGridLayout(gui)
        layout.setSpacing(7)

        self.calculate_table_button = QPushButton('Calculate Table')
        self.calculate_table_button.setStatusTip('Calculate the clinical parameters overview table.')
        layout.addWidget(self.calculate_table_button, 0,2, 1,2)
        self.calculate_table_button.clicked.connect(self.calculate_overview_table)
        
        self.store_table_button = QPushButton('Store Table')
        self.store_table_button.setStatusTip('Store the clinical parameters overview table.')
        layout.addWidget(self.store_table_button, 0,4, 1,2)
        self.store_table_button.clicked.connect(self.store_overview_table)

        self.overview_table = Clinical_Results_Overview_Table()
        self.calculate_overview_table = Clinical_Results_Overview_Table().calculate
        self.overview_TableView = QTableView()
        self.overview_TableView.setModel(self.overview_table.to_pyqt5_table_model())
        self.overview_TableView.resizeColumnsToContents()
        layout.addWidget(self.overview_TableView, 1,2, 10,8)

        self.setLayout(layout)
        layout.setRowStretch(10, 3)
       
    

    def calculate_overview_table(self):
        try:
            self.overview_table.calculate(self.view, self.evals1, self.evals2)
            self.overview_TableView.setModel(self.overview_table.to_pyqt5_table_model())
            self.overview_TableView.resizeColumnsToContents()
            #self.overview_table.df.round(2)
            
        except Exception as e: print(traceback.format_exc())
  
        
    
    def store_overview_table(self):
        storepath, _ = QFileDialog.getSaveFileName(self, "Save Table", "",
                         "CSV(*.csv);;All Files(*.*) ")
 
        if storepath == "":
            return
        """overwrite this function to store the Table's pandas.DataFrame (.df)"""
        pandas.DataFrame.to_csv(self.overview_table.df_original, storepath, sep=';', decimal=',')
        
        return 
        
        