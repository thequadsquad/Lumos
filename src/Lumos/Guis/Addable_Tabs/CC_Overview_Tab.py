from PyQt6.QtWidgets import QMainWindow, QGridLayout, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QTextEdit, QTableView, QTableWidgetItem, QComboBox, QHeaderView, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QDialog, QRadioButton, QButtonGroup, QInputDialog
from PyQt6.QtGui import QIcon, QColor
#from PyQt5.Qt import Qt
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

import pandas

from Lumos.loading_functions import *
from Lumos.Tables  import *
from Lumos.Figures import *
from Lumos         import Views


class CC_CRs_Images_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'Clinical Results and Images/Annotations'
        
    def make_tab(self, gui, view, eva1, eva2):
        self.gui = gui
        self.view = view
        self.eva1 = eva1
        self.eva2 = eva2
        gui.tabs.addTab(self, self.name + ': ' + str(eva1.name))
        layout = self.layout
        layout = QGridLayout(gui)
        layout.setSpacing(7)

        self.cr_table = CC_ClinicalResultsAveragesTable()
        self.cr_table.calculate(self.view, [eva1], [eva2])
        self.cr_tableView = QTableView()
        self.cr_tableView.setModel(self.cr_table.to_pyqt5_table_model())
        layout.addWidget(self.cr_tableView, 0, 0, 1,2)
        
        self.img_fig    = Basic_Presenter()
        self.img_canvas = FigureCanvas(self.img_fig)
        self.img_fig.set_values(view, self.img_canvas, eva1, eva2)
        self.img_fig.visualize(0, 0,0)
        self.img_canvas.mpl_connect('key_press_event', self.img_fig.keyPressEvent)
        self.img_canvas.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.img_canvas.setFocus()
        self.img_toolbar = NavigationToolbar(self.img_canvas, gui)
        layout.addWidget(self.img_canvas,  1,0, 1,1)
        layout.addWidget(self.img_toolbar, 2,0, 1,1)
        
        self.setLayout(layout)
        layout.setRowStretch(1, 3)

    def get_view(self, vname):
        view = [c[1] for c in inspect.getmembers(Views, inspect.isclass) if issubclass(c[1], Views.View) if c[0]==vname][0]
        return view()
    
    def get_view_names(self):
        v_names = [c[0] for c in inspect.getmembers(Views, inspect.isclass) if issubclass(c[1], Views.View) if c[0]!='View']
        return v_names
    
    def select_view(self):
        try:
            view_name = self.combobox_select_view.currentText()
            v         = self.get_view(view_name)
            cc        = copy.deepcopy(self.base_cc)
            self.cc   = Case_Comparison(v.customize_case(cc.case1), v.customize_case(cc.case2))
            cat       = self.cc.case1.categories[0]
            # recalculate CRs and reinitialize Figure
            self.cr_table.calculate([self.cc])
            self.cr_tableView.setModel(self.cr_table.to_pyqt5_table_model())
            self.img_fig.set_values(v, self.cc, self.img_canvas)
            self.img_fig.visualize(0, cat)
        except Exception as e:
            print('Exception in select_view: ', e)


        