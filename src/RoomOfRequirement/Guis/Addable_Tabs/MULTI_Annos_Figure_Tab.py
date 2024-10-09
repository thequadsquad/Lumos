from PyQt6.QtWidgets import QMainWindow, QGridLayout, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QTextEdit, QTableView, QTableWidgetItem, QComboBox, QHeaderView, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QDialog, QRadioButton, QButtonGroup, QInputDialog, QToolBar, QCheckBox, QToolButton, QSizePolicy
from PyQt6.QtGui import QIcon, QColor, QAction, QFont
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

from RoomOfRequirement.Views   import *
from RoomOfRequirement.loading_functions import *
from RoomOfRequirement.Tables  import *
from RoomOfRequirement.Figures import *


class Multi_Annos_One_Figure_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'LGE: Multiple Annotations in one Figure'
        
    def make_tab(self, gui, view, eval_dict):
        self.gui  = gui
        self.view = view
        self.eval_dict = eval_dict
        self.task_dict_checked = copy.copy(eval_dict)
        
        gui.tabs.addTab(self, "Case Figure: "+str(eval_dict[0].name)+ " (Multi Annos)")
        layout = self.layout
        layout = QGridLayout(gui)
        layout.setSpacing(7)


        self.taskname = dict()
        for key, eval in eval_dict.items():
            self.taskname[key] = eval.taskname

        self.toolbar = QToolBar("My main toolbar")
        self.toolbar.setIconSize(QtCore.QSize(1, 16))
        layout.addWidget(self.toolbar, 0,0, 1,16)

        
        back_to_LL_action = QAction("&Back To 2 Reader Comparison", self)
        back_to_LL_action.setStatusTip("Go back to Lazy Luna two Reader Comparison.")
        back_to_LL_action.triggered.connect(self.twotasks_selection)
        
        self.toolbar2 = QToolBar("My second toolbar")
        self.toolbar2.setIconSize(QtCore.QSize(28, 28))
        layout.addWidget(self.toolbar2, 4,14, 1,2)
        fontsize = 13

        b4 = QToolButton(); b4.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b4.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding); b4.setFont(QFont('', fontsize))
        b4.setDefaultAction(back_to_LL_action)
        self.toolbar2.addWidget(b4)

        
        self.combobox_select_contour = QComboBox()
        self.combobox_select_contour.setStatusTip('Choose a Contour')
        self.combobox_select_contour.addItems(['Choose a Contour'] + view.contour_names)
        self.combobox_select_contour.activated.connect(self.recalculate_figure) 
        self.toolbar.addWidget(self.combobox_select_contour)

        
        self.tasklbl = QLabel('Choose Annotations:')
        self.toolbar.addWidget(self.tasklbl)
        
        self.checkbox_dict = dict()
        for eval in eval_dict.values():
            self.checkbox = QCheckBox()
            self.checkbox.setText(eval.taskname)
            self.checkbox.stateChanged.connect(self.update_checked_task_dict)
            self.toolbar.addWidget(self.checkbox)
            self.checkbox_dict[eval.taskname] = self.checkbox
            
        self.evals_list = list()
        for key, eval in self.eval_dict.items():
            self.evals_list.append([self.eval_dict[key]])

        self.p = dict()
        for key in self.task_dict_checked.keys():
            self.p[key] = 0

        
        self.cr_table = Multi_ClinicalResultsAveragesTable()
        self.cr_table.calculate(self.view, self.evals_list)
        self.cr_tableView = QTableView()
        self.cr_tableView.setModel(self.cr_table.to_pyqt5_table_model())
        layout.addWidget(self.cr_tableView, 1, 0, 4,8)
        
        self.annotation_multi_figure = Multi_Annos_in_One()
        self.annotation_multi_canvas = FigureCanvas(self.annotation_multi_figure)
        self.annotation_multi_figure.set_values(view, self.annotation_multi_canvas, self.task_dict_checked)
        self.annotation_multi_figure.visualize(0, self.p, self.eval_dict, list(self.task_dict_checked.keys()), view.contour_names[0])    
        self.annotation_multi_canvas.mpl_connect('key_press_event', self.annotation_multi_figure.keyPressEvent)
        self.annotation_multi_canvas.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.annotation_multi_canvas.setFocus()
        self.annotation_multi_toolbar = NavigationToolbar(self.annotation_multi_canvas, gui)
        layout.addWidget(self.annotation_multi_canvas,  1,8, 3,8)
        layout.addWidget(self.annotation_multi_toolbar, 4,8, 1,6)
        
        self.setLayout(layout)
        layout.setRowStretch(4, 16)
       
    def recalculate_figure(self):
        cont_name = self.combobox_select_contour.currentText()
        if cont_name=='Choose a Contour': return
        try:
            #annocomparison
            d = self.annotation_multi_figure.slice_nr
            p = self.annotation_multi_figure.p
            if self.annotation_multi_figure.clinical_phases and cont_name!=self.annotation_multi_figure.contour_name:
                phase_classes = sorted(list(self.view.clinical_phases[cont_name]))
                self.annotation_multi_figure.clinical_p = phase_classes[0]
                
            self.annotation_multi_figure.visualize(d, p, self.eval_dict, list(self.task_dict_checked.keys()), cont_name)
        except Exception as e: print(traceback.format_exc())


    def update_checked_task_dict(self): 
        for key, eval in self.eval_dict.items():
            chbox = self.checkbox_dict[eval.taskname]
            if chbox.isChecked():
                self.task_dict_checked[key] = eval
            else:
                try:
                    self.task_dict_checked.pop(key)
                except: continue
        
        cont_name = self.combobox_select_contour.currentText()
        if cont_name=='Choose a Contour': return
        try:
            d = self.annotation_multi_figure.slice_nr
            p = self.annotation_multi_figure.p
            self.annotation_multi_figure.visualize(d, p, self.eval_dict, list(self.task_dict_checked.keys()), cont_name)
        except Exception as e: print(traceback.format_exc())
        

    def twotasks_selection(self):
        try:
            self.popup1 = Backto2ReaderComparisonPopup(self)
            self.popup1.show()
        except Exception as e: print(traceback.format_exc()); pass


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
        self.choose_tab.addItems(['Choose a Tab']+[str(tab) for tab in self.view.case_tabs])             
        self.choose_tab.activated.connect(self.open_case_tab)
        self.layout.addWidget(self.choose_tab)
        
        self.choose_reader1 = QComboBox()
        self.choose_reader1.setFixedHeight(50)
        
        helper = list()
        for value in self.parent.taskname.values():
            helper.append(value)
        
        self.choose_reader1.addItems(['Choose Reader 1'] + helper)              
        self.choose_reader1.activated.connect(self.open_case_tab)
        self.layout.addWidget(self.choose_reader1)

        self.choose_reader2 = QComboBox()
        self.choose_reader2.setFixedHeight(50)
        
        self.choose_reader2.addItems(['Choose Reader 2'] + helper)              
        self.choose_reader2.activated.connect(self.open_case_tab)
        self.layout.addWidget(self.choose_reader2)
        
    def open_case_tab(self):
        tab_name = self.choose_tab.currentText()
        reader1  = self.choose_reader1.currentText()
        reader2  = self.choose_reader2.currentText()
        
        if reader1=='Choose Reader 1' or reader2=='Choose Reader 2' or tab_name=='Choose a Tab': return

        for key, value in self.parent.taskname.items():
            if value == reader1:
                eval1 = self.parent.eval_dict[key]
        for key, value in self.parent.taskname.items():
            if value == reader2:
                eval2 = self.parent.eval_dict[key]

        tab  = [v for k,v in self.view.case_tabs.items() if k==tab_name][0]()            
        tab.make_tab(self.parent.gui.parent.tab, self.parent.view, eval1, eval2) 
        self.close()




        
        
      
        
        