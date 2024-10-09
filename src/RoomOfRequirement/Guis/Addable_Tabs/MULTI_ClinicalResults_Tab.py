from PyQt6.QtWidgets import QMainWindow, QGridLayout, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QTextEdit, QTableView, QTableWidgetItem, QComboBox, QHeaderView, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QDialog, QRadioButton, QButtonGroup, QInputDialog, QToolBar, QCheckBox, QToolButton, QSizePolicy
from PyQt6.QtGui import QIcon, QColor, QAction, QFont
#from PyQt6.Qt import Qt
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot, Qt

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


class Multi_ClinicalResults_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'Clinical Results and Backtracking'
        
    def make_tab(self, gui, view, evals_list):
        self.gui = gui
        gui.tabs.addTab(self, "Clinical Results")
        layout = self.layout
        layout = QGridLayout(gui)
        layout.setSpacing(7)

        self.evals_list = evals_list
       
        self.view = view
        self.task_list = []
        for i in range(0,len(evals_list)):
            self.task_list.append(evals_list[i][0].taskname)
        
        back_to_LL_action = QAction("&Back To 2 Reader Comparison", self)
        back_to_LL_action.setStatusTip("Go back to Lazy Luna two Reader Comparison.")
        back_to_LL_action.triggered.connect(self.twotasks_selection)
        
        self.toolbar2 = QToolBar("My second toolbar")
        self.toolbar2.setIconSize(QtCore.QSize(28, 28))
        layout.addWidget(self.toolbar2, 2,14, 1,2)
        fontsize = 13

        b4 = QToolButton(); b4.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b4.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding); b4.setFont(QFont('', fontsize))
        b4.setDefaultAction(back_to_LL_action)
        self.toolbar2.addWidget(b4)

        
        self.crs_TableView = QTableView()
        layout.addWidget(self.crs_TableView, 0,0, 3,8) 
        
        self.multi = MultiBoxplot()
        self.multi_canvas = FigureCanvas(self.multi)
        self.multi.set_view(view); self.multi.set_canvas(self.multi_canvas); self.multi.set_gui(gui)
        self.multi_canvas.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.multi_canvas.setFocus()
        self.multi_toolbar = NavigationToolbar(self.multi_canvas, gui)
        layout.addWidget(self.multi_canvas,  0,8, 2,8)
        layout.addWidget(self.multi_toolbar, 2,8, 1,6)
        layout.setRowStretch(2, 16)
        self.setLayout(layout)
        self.CR_threadworker(view, evals_list)



    def update_figures(self):
        try:
            idx = self.crs_TableView.selectionModel().selectedIndexes()[0]
            row, col = idx.row(), idx.column()
            cr_name = self.crs_table.df['Clinical Result (mean±std)'].iloc[row].split(' ')[0]
            
            try:    self.multi.visualize(cr_name, self.evals_list)
            except: print(traceback.format_exc())
           
        except Exception as e: print(traceback.format_exc())
        
    def CR_threadworker(self, view, evals_list):
        self.worker = CR_Results_Worker(self, view, evals_list)
        self.worker.start()
        self.worker.worksignal.connect(self.update_cr_avgs_table)
        
    def update_cr_avgs_table(self, crs_df):
        self.crs_table    = Multi_ClinicalResultsAveragesTable()
        self.crs_table.df = crs_df
        self.crs_TableView.setModel(self.crs_table.to_pyqt5_table_model())
        self.crs_TableView.selectionModel().selectionChanged.connect(self.update_figures)
        self.crs_TableView.resizeColumnsToContents()

    def twotasks_selection(self):
        try:
            self.popup1 = Backto2ReaderComparisonPopup(self)
            self.popup1.show()
        except Exception as e: print(traceback.format_exc()); pass




class CR_Results_Worker(QThread):
    worksignal = pyqtSignal(pd.DataFrame)

    def __init__(self, parent, view, evals_list):
        super(QThread, self).__init__()
        self.view, self.evals_list = view, evals_list

    @pyqtSlot(pd.DataFrame)
    def run(self):
        self.table = Multi_ClinicalResultsAveragesTable()
        self.table.calculate(self.view, self.evals_list)
        self.worksignal.emit(self.table.df)

        
        
class PresentFailedCasesPopup(QWidget):
    def __init__(self, parent, cr_name):
        super().__init__()
        self.parent = parent
        self.setWindowTitle('Failed Calculations for ' + cr_name)
        self.setGeometry(800, 300, 500, 300)
        self.layout = QVBoxLayout(self)
        self.initUI()

    def initUI(self):
        self.tableView = QTableView()
        failed_rows = self.parent.ba.failed_cr_rows
        df = DataFrame(failed_rows, columns=['case_name', 'studyuid'])
        t = Table(); t.df = df
        self.tableView.setModel(t.to_pyqt5_table_model())
        self.tableView.resizeColumnsToContents()
        self.layout.addWidget(self.tableView)



class Backto2ReaderComparisonPopup(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.view   = self.parent.view
        self.setWindowTitle('Case Tab Selection')
        self.setGeometry(800, 200, 300, 160)
        self.layout = QVBoxLayout(self)
        self.initUI()

    def initUI(self):
        self.choose_tab = QComboBox()
        self.choose_tab.setFixedHeight(50) 
        self.choose_tab.addItems(['Choose a Tab']+[str(tab) for tab in self.view.stats_tabs])              
        self.choose_tab.activated.connect(self.open_stats_tab)
        self.layout.addWidget(self.choose_tab)
        
        self.choose_reader1 = QComboBox()
        self.choose_reader1.setFixedHeight(50)
        
        self.choose_reader1.addItems(['Choose Reader 1'] + [str(self.parent.task_list[i]) for i in range(0, len(self.parent.task_list))])              
        self.choose_reader1.activated.connect(self.open_stats_tab)
        self.layout.addWidget(self.choose_reader1)

        self.choose_reader2 = QComboBox()
        self.choose_reader2.setFixedHeight(50)
        
        self.choose_reader2.addItems(['Choose Reader 2'] + [str(self.parent.task_list[i]) for i in range(0, len(self.parent.task_list))])             
        self.choose_reader2.activated.connect(self.open_stats_tab)
        self.layout.addWidget(self.choose_reader2)
        
    def open_stats_tab(self):
        tab_name = self.choose_tab.currentText()
        reader1  = self.choose_reader1.currentText()
        reader2  = self.choose_reader2.currentText()
       
        if reader1=='Choose Reader 1' or reader2=='Choose Reader 2' or tab_name=='Choose a Tab': return

        for i in range(0, len(self.parent.task_list)):
            if self.parent.task_list[i] == reader1:
                evals1 = self.parent.evals_list[i]
        for i in range(0, len(self.parent.task_list)):
            if self.parent.task_list[i] == reader2:
                evals2 = self.parent.evals_list[i]
        
        tab  = [v for k,v in self.view.stats_tabs.items() if k==tab_name][0]()            
        tab.make_tab(self.parent.gui.parent.tab, self.parent.view, evals1, evals2) 
        self.close()




        




