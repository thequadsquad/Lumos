from PyQt6.QtWidgets import QMainWindow, QGridLayout, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QTextEdit, QTableView, QTableWidgetItem, QComboBox, QHeaderView, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QDialog, QRadioButton, QButtonGroup, QInputDialog, QMessageBox, QToolBar, QSizePolicy, QToolButton, QFrame
from PyQt6.QtGui import QIcon, QColor, QFont, QAction
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QSize
from PyQt6 import QtCore

from pathlib import Path
import copy
import os
import inspect
import traceback

import pandas

from Lumos.loading_functions import *
from Lumos.Tables            import *
from Lumos.Figures           import *
from Lumos                   import Views

class StoreInfoWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self, view, evals_list, view_folder_path, icon_path, storage_type):
        super().__init__()
        self.view                = view
        self.evals_list          = evals_list 
        self.view_folder_path    = view_folder_path
        self.icon_path           = icon_path
        self.storage_type        = storage_type  
        
    def run(self):
        self.view.store_information(self.evals_list, self.view_folder_path, self.icon_path, self.storage_type) 
        self.finished.emit()


class CCs_Multi_Overview_Tab(QWidget):
    def __init__(self, parent, quad, cases_list):
        super().__init__()
        self.parent = parent
        parent.tabs.addTab(self, "Overview")
        self.layout = QGridLayout(self)
        self.layout.setSpacing(7)
        self.layout.setRowStretch(16, 16)
        self.quad = quad
        
        self.cases    = dict() #keys: tasks (as numbers), values: cases for the task
        self.task_id  = dict() #keys: tasks (as numbers), values: task_ids
        self.taskname = dict() #keys: tasks (as numbers), values: task_names 
        
        # visualization dictionary
        self.qualitative_figures = dict()
        
        for i in range(0, len(cases_list)):
            self.cases[i]   = cases_list[i]
            self.task_id[i] = self.cases[i][0].task_id 
        task_list = []
        for i in range(0, len(cases_list)):
            task_list.append(self.quad.task_coll.find_one({'_id': self.task_id[i]}))
        for i in range(0, len(cases_list)):
            self.taskname[i] = task_list[i]['displayname'] 
  
        self.excluded_studyuids = []
        self.threads = []
        self.workers = []

        # actions to connect new tabs with icons 
        statstab_action = QAction(QIcon(os.path.join(self.parent.bp, 'Icons','notebooks.png')), "&Statistics", self)
        statstab_action.setStatusTip("Open Statistical Tab for available case comparisons.")
        statstab_action.triggered.connect(self.statstab_selection)
        
        casetab_action = QAction(QIcon(os.path.join(self.parent.bp, 'Icons','notebook.png')), "&Single Case", self)
        casetab_action.setStatusTip("Open Case Tab for a case comparison.")
        casetab_action.triggered.connect(self.singletab_selection)
        
        export_action = QAction(QIcon(os.path.join(self.parent.bp, 'Icons','disk-return.png')), "&Save Report", self)
        export_action.setStatusTip("Store figures and tables for view.")
        export_action.triggered.connect(self.store_all)

        # Toolbar
        self.toolbar = QToolBar("My main toolbar")
        self.toolbar.setIconSize(QSize(28, 28))
        self.layout.addWidget(self.toolbar, 0,0, 1,16)
        fontsize = 13
        # select view combobox
        self.view_combo = QComboBox()
        self.view_combo.insertItems(1, ["Select View"] + self.get_view_names())
        self.view_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.view_combo.setStatusTip("Select a view on the data.")
        self.toolbar.addWidget(self.view_combo)
        self.view_combo.activated.connect(self.select_view)
        # open statistical tab
        b1 = QToolButton(); b1.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b1.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding); b1.setFont(QFont('', fontsize))
        b1.setDefaultAction(statstab_action)
        self.toolbar.addWidget(b1)
        # open case tab
        b2 = QToolButton(); b2.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b2.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding); b2.setFont(QFont('', fontsize))
        b2.setDefaultAction(casetab_action)
        self.toolbar.addWidget(b2)
        # storage
        b3 = QToolButton(); b3.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b3.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding); b3.setFont(QFont('', fontsize))
        b3.setDefaultAction(export_action)
        self.toolbar.addWidget(b3)
        
        self.layout.addWidget(QHLine(), 1, 0, 1, 16)
        # overview what was selected
        self.selected_view_lbl  = QLabel('View: ')
        self.selected_view_text = QLabel('None')
        self.nr_cases_lbl       = QLabel('Number of Cases: ')
        self.nr_cases_text      = QLabel(str(len(self.cases[0])))  
        #tasks in taskslist 
        for i in self.taskname.keys():
            self.task_lbl          = QLabel('Task ' + str(i+1) + ': ' + str(self.taskname[i]) + '     ')
            if i in range(0,10):
                self.layout.addWidget(self.task_lbl,          2, i+4, 1,1)
            else:
                self.layout.addWidget(self.task_lbl,          3, i-6, 1,1)

        self.layout.addWidget(self.selected_view_lbl,  2, 0, 1,1)
        self.layout.addWidget(self.selected_view_text, 2, 1, 1,1)
        self.layout.addWidget(self.nr_cases_lbl,       2, 2, 1,1)
        self.layout.addWidget(self.nr_cases_text,      2, 3, 1,1)
        
        self.layout.addWidget(QHLine(), 4, 0, 1, 16)

        self.tableView_overview = QTableView(self)
        self.tableView_overview.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.tableView_overview.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.tableView_overview.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.layout.addWidget(self.tableView_overview, 5, 0, 1,16)
    
        # Titles
        self.layout.addWidget(QHLine(), 6, 0, 1, 16)
        self.included_lbl  = QLabel('Included Case Comparisons: ')
        self.excluded_lbl  = QLabel('Excluded Case Comparisons: ')
        self.layout.addWidget(self.included_lbl,  7,  0, 1, 7)
        self.layout.addWidget(self.excluded_lbl,  7, 8, 1, 7)
        self.layout.addWidget(QHLine(), 8,  0, 1, 7)
        self.layout.addWidget(QHLine(), 8, 8, 1, 8)
        
        self.tableView = QTableView(self)
        self.tableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.tableView.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.tableView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.tableView, 9, 0, 10, 7)
        
        b_ex = QPushButton('Exclude >>', self);  b_ex.setToolTip('Exclude Cases');  b_ex.clicked.connect(self.exclude_cases)
        self.layout.addWidget(b_ex,  13, 7, 1,1)
        b_inc = QPushButton('<< Include', self); b_inc.setToolTip('Include Cases'); b_inc.clicked.connect(self.include_cases)
        self.layout.addWidget(b_inc, 14, 7, 1,1)
        
        self.tableView_exclude = QTableView(self)
        self.tableView_exclude.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.tableView_exclude.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.tableView_exclude.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.tableView_exclude, 9, 8, 10, 8)
        
        self.calculate_table_overview()
        self.calculate_exclusion_table()
        self.calculate_table()

        
    def statstab_selection(self):
        try:
            if not self.has_view(): return
            view        = self.get_view(self.view_combo.currentText())
            self.popup1 = StatisticalTabSelectionPopup(self, view)
            self.popup1.show()
        except Exception as e: print(traceback.format_exc()); pass
    
    def singletab_selection(self):
        try:
            if not self.has_view(): return
            view        = self.get_view(self.view_combo.currentText())
            self.popup1 = CaseTabSelectionPopup(self, view)
            self.popup1.show()
        except Exception as e: print(traceback.format_exc()); pass
    
    def store_all(self):
        if not self.has_view(): return
        # set path for storage if not selected already
        if not hasattr(self, 'export_storage_folder_path'): self.set_storage_path()
        try:
            # Information Message for User
            view = self.get_view(self.view_combo.currentText())
            view_folder_path = self.make_view_storage_folder()
        except Exception as e:
            print(traceback.format_exc())
        try:
            # view, 
            self.popup3 = ChooseStorageTypePopup(self, view, view_folder_path)
            self.popup3.show()
        except Exception as e:
            print(traceback.format_exc())


    def select_view(self):
        try:
            view_name = self.view_combo.currentText()
            # table should present whether annotations are present or not...
            view_name = self.view_combo.currentText()
            view_name = view_name.split(' (')[0]

            v = self.get_view(view_name)
            
            tuple = ()
            
            evals_dict = dict()
            for k in range(0, len(self.cases)):
                tuple = tuple + (self.cases[k],)
                evals_dict[k] = list()
                
            zipper = zip(tuple[k] for k in range(0,len(self.cases)))
            print(zipper)
            for cs in zipper:
                tmp_view_name = view_name
                for j in range(0,len(cs[0])):
                    if not (tmp_view_name in cs[0][j].evals.keys()): continue
                    print(cs[0][j].evals[tmp_view_name])
                    if not (len(cs[0][j].evals[tmp_view_name])!=0): continue
                    k = list(self.taskname.values()).index(cs[0][j].evals[tmp_view_name][0].taskname)
                    evals_dict[k].append(cs[0][j].evals[tmp_view_name][0]) 
                    
            
            self.evals_list = [evals_dict[j] for j in evals_dict.keys()]       
            self.excluded_studyuids = set()
            self.calculate_table_overview()
            self.calculate_exclusion_table()
            self.calculate_table()
            self.selected_view_text.setText(view_name)
            self.nr_cases_text.setText(str(len(self.cases[0])))
            if view_name not in self.qualitative_figures.keys(): self.qualitative_figures[view_name] = []
        except Exception as e:
            print(traceback.format_exc())
    
    def get_view(self, vname):
        vname = vname.split(' (')[0] 
        view = [c[1] for c in inspect.getmembers(Views, inspect.isclass) if issubclass(c[1], Views.View) if c[0]!='View' and c[1]().name==vname][0] 
        return view()
    
    def get_view_names(self):
        v_names = [c[1]().name for c in inspect.getmembers(Views, inspect.isclass) if issubclass(c[1], Views.View) if c[0]!='View']
        nr_ccs_per_view = {v:0 for v in v_names}

        try:
            tuple = ()
            if len(self.cases) in range(1,20):
                for k in range(0, len(self.cases)):
                    tuple = tuple + (self.cases[k],)

            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText("Please choose between 1 and 20 methods.")
                msg.setInformativeText("You have to choose at least one and no more than twenty methods.")
                retval = msg.exec()

            zipper = list(zip(tuple[k] for k in range(0,len(self.cases))))
            
            list_of_sets = [[set(cs[0][j].evals.keys() ) for j in range(0,len(tuple[0])) ] for cs in zipper ]
           
            inter_sets   = []
            for k in range(0, len(list_of_sets[0])):
                inter_sets.append([list_of_sets[i][k] for i in range(0, len(list_of_sets)) ])
            j=0 # index for number of cases we walk through
            for lists in inter_sets:
                for vname in set.intersection( *lists ):
                    if 0 in [len(cs[0][j].evals[vname] )   for cs in zipper]: continue
                    vname = vname.replace('Lazy Luna: ', '')
                    nr_ccs_per_view[vname] += 1
                j+=1
        except Exception as e:
            print(traceback.format_exc())
            
        v_names = [v+' ('+str(nr_ccs_per_view[v])+')' for v in v_names]
        return v_names

    
    def calculate_table_overview(self):
        view_name  = self.view_combo.currentText()
        view_name  = view_name.split(' (')[0]
        cols, rows = ['Nr of Cases']+['Age (Y)','Gender (F/M)','Weight (kg)','Height (m)'], []                                             
        for c0 in self.cases[0]:
            tmp_view_name = view_name
            if not tmp_view_name in c0.evals.keys(): continue 
            _, age, gender, weight, height = c0.get_patient_info()
            try:    a = float(age)
            except: a = np.nan
            try:    w = float(weight)
            except: w = np.nan
            try:    h = float(height)
            except: h = np.nan
            row = [a, gender, w, h]
            rows.append(row)
        Fs, Ms = sum([1 for r in rows if r[1]=='F']), sum([1 for r in rows if r[1]=='M'])
        avgs = [[len(rows), np.around(np.nanmean([r[0] for r in rows]), 2), str(Fs)+'/'+str(Ms), 
                 np.around(np.nanmean([r[2] for r in rows]), 2), np.around(np.nanmean([r[3] for r in rows]), 2)]]
        self.overview_table = Table()
        try:    self.overview_table.df = pandas.DataFrame(avgs, columns=cols)
        except: self.overview_table.df = pandas.DataFrame([['' for _ in range(len(cols))]], columns=cols)
        self.tableView_overview.setModel(self.overview_table.to_pyqt5_table_model())
        
    
    def calculate_table(self):
        try:
            view_name  = self.view_combo.currentText()
            view_name  = view_name.split(' (')[0]
            cols, rows = ['Case Name','Age (Y)','Gender (F/M)','Weight (kg)','Height (m)','Studyuid'], []                  
            excluded_studyuids = set(self.excluded_studyuids)
            for c0 in self.cases[0]:
                tmp_view_name = view_name
                if not tmp_view_name in c0.evals.keys() : continue   
                if c0.studyuid in excluded_studyuids: continue
                name, age, gender, weight, height = c0.get_patient_info()
                row = [name, age, gender, weight, height, c0.studyuid]
                rows.append(row)
            t  = Table()
            t.df = pandas.DataFrame(rows, columns=cols)
            self.tableView.setModel(t.to_pyqt5_table_model())
            self.tableView.resizeColumnsToContents()
        except Exception as e: print(traceback.format_exc())
        
                  
    def calculate_exclusion_table(self):
        try:
            view_name = self.view_combo.currentText()
            view_name = view_name.split(' (')[0]
            cols, rows = ['Case Name','Age (Y)','Gender (F/M)','Weight (kg)','Height (m)','Studyuid'], []                   
            excluded_studyuids = set(self.excluded_studyuids)
            for c0 in self.cases[0]:
                tmp_view_name = view_name
                if not tmp_view_name in c0.evals.keys(): continue 
                if not c0.studyuid in excluded_studyuids: continue
                name, age, gender, weight, height = c0.get_patient_info()
                row = [name, age, gender, weight, height, c0.studyuid]
                rows.append(row)
            t    = Table()
            t.df = pandas.DataFrame(rows, columns=cols)
            self.tableView_exclude.setModel(t.to_pyqt5_table_model())
            self.tableView_exclude.resizeColumnsToContents()
        except Exception as e: print(traceback.format_exc())
        
    
    def exclude_cases(self):
        try:
            idxs = self.tableView.selectionModel().selectedRows(column=5)
            new_studyuid_exclusions = [self.tableView.selectionModel().model().data(idx) for idx in idxs]
            self.excluded_studyuids = list(set(self.excluded_studyuids).union(set(new_studyuid_exclusions)))
            self.calculate_table()
            self.calculate_exclusion_table()
            self.calculate_table_overview()
        except Exception as e: print(traceback.format_exc())
    
    def include_cases(self):
        try:
            idxs = self.tableView_exclude.selectionModel().selectedRows(column=5)
            new_studyuid_inclusions = [self.tableView_exclude.selectionModel().model().data(idx) for idx in idxs]
            for suid in new_studyuid_inclusions: self.excluded_studyuids.remove(suid)
            self.calculate_table()
            self.calculate_exclusion_table()
            self.calculate_table_overview()
        except Exception as e: print(traceback.format_exc())
    
    def has_view(self):
        if self.view_combo.currentText()!='Select View': return True
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("You must select a View first.")
        retval = msg.exec()
        return False
    
    def set_storage_path(self):
        try:   self.export_storage_folder_path = QFileDialog(self, '').getExistingDirectory()
        except Exception as e: print(traceback.format_exc())
    
    def make_view_storage_folder(self):
        try:
            taskname1 = self.taskname1
            taskname2 = self.taskname2
            export_folder_path = os.path.join(self.export_storage_folder_path, 'Export_comparison_'+taskname1+'_'+taskname2)
            if not os.path.exists(export_folder_path): os.mkdir(export_folder_path)
            view_name = self.view_combo.currentText().split(' (')[0]
            view = self.get_view(view_name)
            view_folder_path = os.path.join(export_folder_path, view_name)
            if not os.path.exists(view_folder_path): os.mkdir(view_folder_path)
            return view_folder_path
        except Exception as e: print(traceback.format_exc())
    
    def end_storage_message(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Finished calculating storable information.")
        msg.setWindowTitle("Storage Calcuations DONE")
        retval = msg.exec_()
        pass
    
    def open_title_and_comments_popup(self, fig, fig_name):
        view = self.get_view(self.view_combo.currentText())
        self.popup1 = TitleAndCommentsPopup(self, view, fig, fig_name)
        self.popup1.show()
        

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


class StatisticalTabSelectionPopup(QWidget):
    def __init__(self, parent, view):
        super().__init__()
        self.parent = parent
        self.view   = view
        self.setWindowTitle('Statistical Tab Selection')
        self.setGeometry(800, 200, 300, 160)
        self.layout = QVBoxLayout(self)
        self.initUI()

    def initUI(self):
        self.warning_lbl = QLabel("You're calculating statistics for "+str(len(self.parent.evals_list[0]))+" cases. Calculations may take several minutes.")
        self.warning_lbl.setWordWrap(True)
        self.layout.addWidget(self.warning_lbl)
        
        self.choose_tab = QComboBox()
        self.choose_tab.setFixedHeight(50)
        self.choose_tab.addItems(['Choose a Tab']+[str(tab) for tab in self.view.multi_stats_tabs])             
        self.layout.addWidget(self.choose_tab)
        
        self.stats_button = QPushButton('Open StatsTab')
        self.layout.addWidget(self.stats_button)
        self.stats_button.clicked.connect(self.open_statistical_tab)
        
    def open_statistical_tab(self):
        tab_name = self.choose_tab.currentText()
        tab  = [v for k,v in self.view.multi_stats_tabs.items() if k==tab_name][0]()                           
        evals_list = self.parent.evals_list  
        evals_list_stats = dict()
        for i in range(0, len(evals_list)):
            evals_list_stats[i] = [e for e in evals_list[i] if e.studyuid not in self.parent.excluded_studyuids]          
        
        tab.make_tab(self.parent.parent.parent.tab, self.view, evals_list_stats)                                        
        self.close()
        
        
class CaseTabSelectionPopup(QWidget):
    def __init__(self, parent, view):
        super().__init__()
        self.parent = parent
        self.view   = view
        self.setWindowTitle('Case Tab Selection')
        self.setGeometry(800, 200, 300, 160)
        self.layout = QVBoxLayout(self)
        self.initUI()

    def initUI(self):
        self.choose_tab = QComboBox()
        self.choose_tab.setFixedHeight(50)
        self.choose_tab.addItems(['Choose a Tab']+[str(tab) for tab in self.view.multi_case_tabs])              
        self.choose_tab.activated.connect(self.open_case_tab)
        self.layout.addWidget(self.choose_tab)
        
        self.choose_case = QComboBox()
        self.choose_case.setFixedHeight(50)
        casenames = [e.name for e in set(self.parent.evals_list[0]).union(set(self.parent.evals_list[0]))      
                     if e.studyuid not in self.parent.excluded_studyuids]
        sorted_casenames = sorted(casenames, key=str.lower)                                         
        self.choose_case.addItems(['Choose a Case'] + sorted_casenames)             
        self.choose_case.activated.connect(self.open_case_tab)
        self.layout.addWidget(self.choose_case)
        
    def open_case_tab(self):
        tab_name = self.choose_tab.currentText()
        casename = self.choose_case.currentText()
        if casename=='Choose a Case' or tab_name=='Choose a Tab': return
        
        eval_dict = dict()
        for i in range(0, len(self.parent.evals_list)):
            eval_dict[i] = [eva for eva in self.parent.evals_list[i] if eva.name==casename][0]     
            
        tab  = [v for k,v in self.view.multi_case_tabs.items() if k==tab_name][0]()                   
        tab.make_tab(self.parent.parent.parent.tab, self.view, eval_dict)
        self.close()


     
# for tracing differences
class TitleAndCommentsPopup(QWidget):
    def __init__(self, parent, view, fig, fig_name):
        super().__init__()
        self.parent   = parent
        self.view     = view
        self.fig      = fig
        self.fig_name = fig_name
        self.setWindowTitle('Figure Comments')
        self.setGeometry(800, 200, 300, 120)
        self.layout = QVBoxLayout(self)
        self.initUI()

    def initUI(self):
        self.title = QLineEdit('- Title - ')
        self.layout.addWidget(self.title)
        self.comment = QLineEdit('- Comments -')
        self.layout.addWidget(self.comment)
        self.store_figure_button = QPushButton('Store Figure')
        self.layout.addWidget(self.store_figure_button)
        self.store_figure_button.clicked.connect(self.store_figure)
        
    def store_figure(self):
        if not hasattr(self.parent, 'export_storage_folder_path'): self.parent.set_storage_path()
        view_folder_path = self.parent.make_view_storage_folder()
        qf_path = os.path.join(view_folder_path, 'Qualitative_figures')
        if not os.path.exists(qf_path): os.mkdir(qf_path)
        fig_path  = self.fig.store(qf_path)
        view_name = self.parent.view_combo.currentText().split(' (')[0]
        self.parent.qualitative_figures[view_name].append([self.title.text()+' '+self.fig_name, fig_path, self.comment.text()])
        self.close()

        
# For Storage for trainees or AIs
class ChooseStorageTypePopup(QWidget):
    def __init__(self, parent, view, view_folder_path):
        super().__init__()
        self.parent = parent
        self.view   = view
        self.view_folder_path = view_folder_path
        self.setWindowTitle('Customize Comparison Export')
        self.setGeometry(800, 200, 300, 120)
        self.layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout(self)
        self.initUI()

    def initUI(self):
        self.layout.addWidget(QLabel('Calculations may take several minutes. Another pop-up will inform you of calculation end.'))
        self.layout.addWidget(QLabel('To abort export click "Cancel".'))
        self.layout.addWidget(QLabel('Otherwise: select a Comparison Export.'))
        
        self.layout.addLayout(self.button_layout)
        self.simple_store_button = QPushButton('Simple Export')
        self.button_layout.addWidget(self.simple_store_button)
        self.simple_store_button.clicked.connect(self.simple_store)
        self.extensive_store_button = QPushButton('Extensive Export')
        self.button_layout.addWidget(self.extensive_store_button)
        self.extensive_store_button.clicked.connect(self.extensive_store)
        
        
        self.abort_button = QPushButton('Cancel')
        self.button_layout.addWidget(self.abort_button)
        self.abort_button.clicked.connect(self.abort)
        
    def simple_store(self):
        self.storage_type = 0
        self.store()
        self.close()
        
    def extensive_store(self):
        self.storage_type = 1
        self.store()
        self.close()
        
    def abort(self):
        self.close()
        
    def store(self):
        try:   self.parent.overview_table.store(os.path.join(self.view_folder_path, 'overview_table.csv'))
        except Exception as e: print(traceback.format_exc())
        try:
            self.view.store_information(self.parent.evals1, self.parent.evals2, self.view_folder_path, 
                                        os.path.join(self.parent.parent.bp, 'Icons'), self.storage_type)
            """
            self.parent.threads.append(QThread())
            self.parent.workers.append(StoreInfoWorker(self.view, self.parent.evals1, self.parent.evals2, self.view_folder_path, os.path.join(self.parent.parent.bp, 'Icons'), self.storage_type))
            thread, worker = self.parent.threads[-1], self.parent.workers[-1]
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            thread.finished.connect(self.parent.end_storage_message)
            thread.start()
            """
        except Exception as e:
            print(traceback.format_exc())