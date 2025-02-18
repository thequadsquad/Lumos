from PyQt6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QApplication, QLabel, QToolBar, QStatusBar, QStyle, QCheckBox, QGridLayout, QPushButton, QLineEdit, QFrame, QTableView, QHeaderView, QFileDialog, QDialog, QToolButton, QSizePolicy, QInputDialog, QMessageBox, QComboBox
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

from RoomOfRequirement.Tables import Table
from RoomOfRequirement import Views
from RoomOfRequirement.loading_functions import *

from RoomOfRequirement.Quad import *
from RoomOfRequirement.Case import *



###################################################################################################
###################################################################################################
## Might consider instead providing the tabs for each cohort and then opening two tables beneath ##
## First Table: For all the cases
## Second Table: For the Tasks which as associated with any of the SUIDs with:
##               How many cases overlap between Cohort SUIDs and Task SUIDs
## Then the User could doubleclick a task for comparison
###################################################################################################
###################################################################################################


class Database_TabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.bp     = parent.bp
        self.layout = QVBoxLayout(self)
        self.tabs   = QTabWidget()
        self.tab1   = QWidget()
        self.tabs.resize(self.parent.width, self.parent.height)
        
        self.quad = QUAD_Manager()
        
        # Add tabs
        self.tabs.addTab(self.tab1, "Selection Process")
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(lambda index: self.tabs.removeTab(index))
        
        ##################
        ## Create TAB 1 ##
        ##################
        self.tab1.layout = QGridLayout(self)
        self.tab1.layout.setSpacing(7)
        
        open_action = QAction(QIcon(os.path.join(self.parent.bp, 'Icons','eye.png')), "&Open Overview", self)
        open_action.setStatusTip("Open Overview of all selected Case Comparisons.")
        open_action.triggered.connect(self.open_case_comparison_overview)
        
        # Menubar
        #menu = self.parent.menuBar()
        #file_menu = menu.addMenu("&Database")
        #file_menu.addAction(show_help)
        
        # Toolbar
        self.toolbar = QToolBar("My main toolbar")
        self.toolbar.setIconSize(QSize(28, 28))
        self.tab1.layout.addWidget(self.toolbar, 0,0, 1,3)
        fontsize = 13
        #b1 = QToolButton(); b1.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        #b1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding); b1.setFont(QFont('', fontsize))
        #b1.setDefaultAction(connect_action)
        #self.toolbar.addWidget(b1)
        self.combo=QComboBox()
        self.combo.insertItems(1,["Select Reader"])
        self.combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.combo.setStatusTip("Select the first reader.")
        self.toolbar.addWidget(self.combo)
        self.combo2=QComboBox()
        self.combo2.insertItems(1,["Select Reader"])
        self.combo2.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.combo2.setStatusTip("Select the second reader.")
        self.toolbar.addWidget(self.combo2)
        b2 = QToolButton(); b2.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b2.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding); b2.setFont(QFont('', fontsize))
        b2.setDefaultAction(open_action)
        self.toolbar.addWidget(b2)
        
        self.tab1.layout.addWidget(QHLine(), 1, 0, 1, 3)
        
        self.tableview_tabs = QTabWidget()
        self.tableview_tabs.setStatusTip("Table of cases belonging to tabs.")
        self.tab1.layout.addWidget(self.tableview_tabs, 4,0, 1,3)
        self.tableview_tabs.currentChanged.connect(self.set_available_readers)
        
        self.update_tableview_tabs()
        
        # set layout
        self.tab1.setLayout(self.tab1.layout)
        self.tab1.layout.setRowStretch(4, 5)
        
        self.layout.addWidget(self.tabs)
        
        
    def set_available_readers(self):
        # use tabname for reader name extraction from database
        # add names to combobox
        tabname = self.tableview_tabs.tabText(self.tableview_tabs.currentIndex())
        cohort  = self.quad.coho_coll.find_one({'name': tabname})
        tasks = list(self.quad.task_coll.find({"studyuids": {"$in": cohort['studyuids']}}))
        self.task_ids = [t['_id'] for t in tasks]
        tasknames = ['Select Task'] + [t['displayname'] for t in tasks] #[r['firstname']+' '+r['lastname'] for r in readers]
        self.combo.clear()
        self.combo.addItems(tasknames)
        self.combo2.clear()
        self.combo2.addItems(tasknames)
    
            
    def open_case_comparison_overview(self):
        if not self.has_readers(): return
        # gather the Case Comparisons
        tabname = self.tableview_tabs.tabText(self.tableview_tabs.currentIndex())
        cohort  = self.quad.coho_coll.find_one({'name': tabname})
        task1, task2 = self.task_ids[self.combo.currentIndex()-1], self.task_ids[self.combo2.currentIndex()-1]
        task1 = self.quad.task_coll.find_one({'_id': task1})
        task2 = self.quad.task_coll.find_one({'_id': task2})
        
        cases = list(self.quad.case_coll.find({'$and': [{'studyuid': {'$in': cohort['studyuids']}},
                                                        {'studyuid': {'$in': task1['studyuids']}},
                                                        {'studyuid': {'$in': task2['studyuids']}}]}))
        cases = [Case(self.quad, studyuid=c['studyuid']) for c in cases]
        cases1, cases2 = [], []
        for case in cases:
            cases1.append(case.get_imgos_evals_case(task_id=task1['_id']))
            cases2.append(case.get_imgos_evals_case(task_id=task2['_id']))
        cases1, cases2 = sorted(cases1, key=lambda c: c.name), sorted(cases2, key=lambda c: c.name)
        self.parent.add_ccs_overview_tab(self.quad, cases1, cases2)
            
    
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
        cases = self.quad.case_coll.find({'studyuid': {'$in': cohort['studyuids']}})
        rows = sorted([[c['name'], c['age'], c['gender'], c['weight'], c['height'], c['studyuid']] for c in cases], key=lambda c: c[0])
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
        reader1, reader2 = self.combo.currentText(), self.combo2.currentText()
        if reader1!='Select Reader' and reader2!='Select Reader': return True
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Missing Readers.")
        msg.setInformativeText("Select two readers first.")
        retval = msg.exec_()
        return False
    
    def has_cases(self, iterable):
        # Information Message for User
        if len(iterable)!=0: return True
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("No cases.")
        msg.setInformativeText("The selected readers share no cases. Select different readers.")
        retval = msg.exec_()
        return False
    

        
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
