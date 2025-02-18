from PyQt6.QtWidgets import QMainWindow, QGridLayout, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QTextEdit, QTableView, QTableWidgetItem, QComboBox, QHeaderView, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QDialog, QRadioButton, QButtonGroup, QInputDialog, QMessageBox
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


class CCs_Metrics_OverviewTable_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'CCs_Metrics_OverviewTable_Tab'
        
    def make_tab(self, gui, view, evals1, evals2): 
        self.gui  = gui
        self.view = view
        self.evals1, self.evals2 = evals1, evals2
        gui.tabs.addTab(self, "Metrics Overview Table")
        layout = self.layout
        layout = QGridLayout(gui)
        layout.setSpacing(7)

        self.combobox_select_contour = QComboBox()
        self.combobox_select_contour.setStatusTip('Choose a Contour')
        self.combobox_select_contour.addItems(['Choose a Contour'] + view.contour_names)
        self.combobox_select_contour.activated.connect(self.calculate_metrics_overview_table) 
        layout.addWidget(self.combobox_select_contour, 0,0, 1,2)
        
        
        self.calculate_table_button = QPushButton('Calculate Table')
        self.calculate_table_button.setStatusTip('Calculate the metrics overview table.')
        layout.addWidget(self.calculate_table_button, 0,4, 1,2)
        self.calculate_table_button.clicked.connect(self.calculate_metrics_overview_table)
        
        self.store_table_button = QPushButton('Store Table')
        self.store_table_button.setStatusTip('Store the metrics overview table.')
        layout.addWidget(self.store_table_button, 0,6, 1,2)
        self.store_table_button.clicked.connect(self.store_metrics_overview_table)

        self.metrics_overview_table = Metrics_Overview_Table()
        self.calculate_metrics_overview_table = Metrics_Overview_Table().calculate
        self.metrics_overview_TableView = QTableView()
        self.metrics_overview_TableView.setModel(self.metrics_overview_table.to_pyqt5_table_model())
        self.metrics_overview_TableView.resizeColumnsToContents()
        layout.addWidget(self.metrics_overview_TableView, 1,2, 10,8)

        self.setLayout(layout)
        layout.setRowStretch(10, 3)
       
    

    def calculate_metrics_overview_table(self):
        cont_name = self.combobox_select_contour.currentText()
        if cont_name=='Choose a Contour': 
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setInformativeText("Please choose a contour to calculate the metrics overview table.")
            msg.setText("No contour name")
            retval = msg.exec()
            return
        try:
            self.metrics_overview_table.calculate(self.view, cont_name, self.evals1, self.evals2)
            self.metrics_overview_TableView.setModel(self.metrics_overview_table.to_pyqt5_table_model())
            self.metrics_overview_TableView.resizeColumnsToContents()
            #self.metrics_overview_table.df.round(2)
            
        except Exception as e: print(traceback.format_exc())
  
        
    
    def store_metrics_overview_table(self):
        storepath, _ = QFileDialog.getSaveFileName(self, "Save Table", "",
                         "CSV(*.csv);;All Files(*.*) ")
 
        if storepath == "":
            return
        #"""overwrite this function to store the Table's pandas.DataFrame (.df)"""
        pandas.DataFrame.to_csv(self.metrics_overview_table.df_original, storepath, sep=';', decimal=',')
        
        return 
        
        