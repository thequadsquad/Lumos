from PyQt6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QApplication, QLabel, QToolBar, QStatusBar, QStyle, QCheckBox, QGridLayout, QPushButton, QLineEdit, QFrame, QTableView, QHeaderView, QFileDialog, QDialog, QToolButton, QSizePolicy, QInputDialog, QMessageBox, QComboBox, QScrollArea
from PyQt6.QtGui import QIcon, QColor, QPalette, QFont, QAction
from PyQt6.QtCore import Qt, QSize, QDir, QSortFilterProxyModel, QSettings
from PyQt6 import QtCore

import os
from pathlib import Path
import sys
import pandas
import traceback
import inspect
import copy

from Lumos.Tables import Table
from Lumos.Views import *
from Lumos.loading_functions import *

from Lumos.Quad import *
from Lumos.Case import *



###################################################################################################
###################################################################################################
##  Selection Tab - finds evals from database (quad manager) for selected tasks                  ##
##                - connection to overview tab                                                   ##
###################################################################################################
###################################################################################################


class Multi_Database_TabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.bp     = parent.bp
        self.layout = QVBoxLayout(self)
        self.tabs   = QTabWidget()
        self.tab1   = QWidget()
        self.tabs.resize(self.parent.width, self.parent.height)
        
        self.quad = QUAD_Manager()
        
        # Add Tabs
        self.tabs.addTab(self.tab1, "Selection Process")
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(lambda index: self.tabs.removeTab(index))
        
        ##################################
        ## Create Tab 1 (Selection Tab) ##
        ##################################
        self.tab1.layout = QGridLayout(self)
        self.tab1.layout.setSpacing(7)
        
        # Toolbar
        self.toolbar = QToolBar("My main toolbar")
        self.toolbar.setIconSize(QSize(28, 28))
        self.tab1.layout.addWidget(self.toolbar, 0,0, 3,3)
        
        self.tab1.layout.addWidget(QHLine(), 1, 0, 4, 3)
        
        self.tableview_tabs = QTabWidget()
        self.tableview_tabs.setStatusTip("Table of cases belonging to tabs.")
        self.tab1.layout.addWidget(self.tableview_tabs, 4,0, 4,3)
        self.tableview_tabs.currentChanged.connect(self.set_available_readers)
        
        self.update_tableview_tabs()

        # set layout
        self.tab1.setLayout(self.tab1.layout)
        self.tab1.layout.setRowStretch(4, 5)
        
        self.layout.addWidget(self.tabs)
        
        
    def set_available_readers(self):
        # use tabname (i.e. cohort name) for reader name extraction from database (find all tasks associated with cohort)
        # add names to toolbar as qcheckboxes
        tabname = self.tableview_tabs.tabText(self.tableview_tabs.currentIndex())
        cohort  = self.quad.coho_coll.find_one({'name': tabname})
        self.tasks = list(self.quad.task_coll.find({"studyuids": {"$in": cohort['studyuids']}}))
        
        self.task_ids = [t['_id'] for t in self.tasks]
        self.tasknames = [t['displayname'] for t in self.tasks] 
        self.toolbar.clear()
        # add widgets to Toolbar 
        self.tasklbl = QLabel('Select Tasks:')
        self.toolbar.addWidget(self.tasklbl)
        self.checkbox_dict = dict()
        for t in self.tasks:
            try:
                self.checkbox = QCheckBox()
                self.checkbox.setText(t['displayname'])
                self.checkbox.stateChanged.connect(self.has_readers) #self.test
                
                self.toolbar.addWidget(self.checkbox)
                self.checkbox_dict[t['_id']] = self.checkbox
                
            except: continue
        # Connection Overview Tab
        self.open_action = QAction(QIcon(os.path.join(self.parent.bp, 'Icons','eye.png')), "&Open Overview", self)
        self.open_action.setStatusTip("Open Overview of all selected Case Comparisons.")
        self.open_action.triggered.connect(self.open_case_multi_comparison_overview)
        fontsize = 13
        self.b2 = QToolButton(); self.b2.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.b2.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding); self.b2.setFont(QFont('', fontsize))
        self.b2.setDefaultAction(self.open_action)
        self.toolbar.addWidget(self.b2)

            
    def open_case_multi_comparison_overview(self):
        if not self.has_readers(): return
        # gather the Case Comparisons
        tabname = self.tableview_tabs.tabText(self.tableview_tabs.currentIndex())
        cohort  = self.quad.coho_coll.find_one({'name': tabname})
        task_list = list()
        for t in self.tasks:
            if self.checkbox_dict[t['_id']].isChecked():
                task_list.append(t)
        # only allow btw 1 and 20 tasks 
        if len(task_list)in range(1,20):
            study_uids = {'studyuid': {'$in': cohort['studyuids']}}
            for task in task_list:
                study_uids = {'$and': [study_uids, {'studyuid': {'$in': task['studyuids']}} ]}
            cases =  list(self.quad.case_coll.find(study_uids))
            
            cases = [Case(self.quad, studyuid=c['studyuid']) for c in cases]
            cases_dict = dict()
            for task in task_list:
                cases_dict[task['_id']] = list()
                for case in cases:
                    cases_dict[task['_id']].append((case.get_imgos_evals_case(task_id=task['_id'])))
                #print(cases_dict)
                cases_dict[task['_id']] = sorted(cases_dict[task['_id']], key=lambda c: c.name)
            cases_list= []
            for task in task_list:
                cases_list.append(cases_dict[task['_id']])
            #open overview tab for gathered cases
            self.parent.add_ccs_overview_tab(self.quad, cases_list)
        else: 
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Please choose between 1 and 20 methods.")
            msg.setInformativeText("You have to choose at least one and no more than twenty methods.")
            retval = msg.exec()
            return
          
    
    def update_tableview_tabs(self):
        cohorts = [c for c in self.quad.coho_coll.find()]
        self.tabname_to_tableview = dict()
        self.tabname_to_table     = dict()
        self.tabname_to_proxy     = dict()
        try: 
            for i in range(len(self.tableview_tabs)): self.tableview_tabs.removeTab(0)
        except Exception as e: print(e); pass
        for c in cohorts:
            tabname = c['name']
            self.tabname_to_tableview[tabname] = QTableView()
            self.tabname_to_tableview[tabname].setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
            self.tabname_to_tableview[tabname].setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
            self.tableview_tabs.addTab(self.tabname_to_tableview[tabname], tabname)
            self.present_table_view(c)

    
    def present_table_view(self, cohort):
        tabname = cohort['name']
        cases   = self.quad.case_coll.find({'studyuid': {'$in': cohort['studyuids']}})
        rows    = [[c['name'], c['age'], c['gender'], c['weight'], c['height'], c['studyuid']] for c in cases]
        columns = ['Case Name','Age (Y)','Gender (M/F)','Weight (kg)','Height (m)','StudyUID']
        t  = Table(); t.df = pandas.DataFrame(rows, columns=columns)
        self.tabname_to_tableview[tabname].setModel(t.to_pyqt5_table_model())
        self.tabname_to_table[tabname] = t
        self.tabname_to_tableview[tabname].resizeColumnsToContents()
        proxy_model = QSortFilterProxyModel() 
        proxy_model.setFilterKeyColumn(-1) # Search all columns.
        proxy_model.setSourceModel(t.to_pyqt5_table_model())
        self.tabname_to_proxy[tabname] = proxy_model
        self.tabname_to_tableview[tabname].setModel(self.tabname_to_proxy[tabname])
    
    def has_readers(self):
        # Information Message for User
        task_list = list()
        for t in self.tasks:
            if self.checkbox_dict[t['_id']].isChecked():
                task_list.append(t)
        if len(task_list) != 0: return True
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("Missing Readers.")
        msg.setInformativeText("Select readers first.")
        retval = msg.exec()
        return False
    
    def has_cases(self, iterable):
        # Information Message for User
        if len(iterable)!=0: return True
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("No cases.")
        msg.setInformativeText("The selected readers share no cases. Select different readers.")
        retval = msg.exec()
        return False
    

        
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
