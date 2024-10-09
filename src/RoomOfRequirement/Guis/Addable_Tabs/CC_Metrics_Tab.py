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

from RoomOfRequirement.Views   import *
from RoomOfRequirement.loading_functions import *
from RoomOfRequirement.Tables  import *
from RoomOfRequirement.Figures import *


class CC_Metrics_Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.name = 'Metric Table and Figure'
        
    def make_tab(self, gui, view, eval1, eval2):
        self.gui  = gui
        self.view = view
        self.eval1, self.eval2 = eval1, eval2
        gui.tabs.addTab(self, "Case Metrics: "+str(eval1.name))
        layout = self.layout
        layout = QGridLayout(gui)
        layout.setSpacing(7)
        
        self.combobox_select_contour = QComboBox()
        self.combobox_select_contour.setStatusTip('Choose a Contour')
        self.combobox_select_contour.addItems(['Choose a Contour'] + view.contour_names)
        self.combobox_select_contour.activated.connect(self.recalculate_figure) 
        layout.addWidget(self.combobox_select_contour, 0,0, 1,2)
        
        self.update_table_button = QPushButton('Update Table')
        self.update_table_button.setStatusTip('Update the metrics table for current phase and contour.')
        layout.addWidget(self.update_table_button, 0,2, 1,2)
        self.update_table_button.clicked.connect(self.recalculate_metrics_table)
        
        self.contourname_lbl = QLabel('Contour: '); layout.addWidget(self.contourname_lbl, 1,0, 1,1)
        self.phases_lbl = QLabel('Phases: ');       layout.addWidget(self.phases_lbl,      2,0, 1,1)
        self.equalphases_lbl = QLabel('');          layout.addWidget(self.equalphases_lbl, 3,0, 1,1)
        
        #if type(view) in [SAX_CINE_View, SAX_CS_View, SAX_LGE_View]:
        #    self.metrics_table  = SAX_CINE_CC_Metrics_Table()
        #elif type(view) in [SAX_T1_PRE_View, SAX_T1_POST_View]:
        #    self.metrics_table  = T1_CC_Metrics_Table()
        #elif type(view) in [SAX_T2_View]:
        #    self.metrics_table  = T2_CC_Metrics_Table()
        #else: # type(view) is LAX_CINE_View:
        #    self.metrics_table  = LAX_CC_Metrics_Table()
        self.metrics_table = Metrics_Table()
        
        self.metrics_TableView = QTableView()
        self.metrics_TableView.setModel(self.metrics_table.to_pyqt5_table_model())
        self.metrics_TableView.resizeColumnsToContents()
        layout.addWidget(self.metrics_TableView, 1,2, 10,8)
        
        self.annotation_comparison_figure = Annotation_Comparison()
        self.annotation_comparison_canvas = FigureCanvas(self.annotation_comparison_figure)
        self.annotation_comparison_figure.set_values(view, self.annotation_comparison_canvas, eval1, eval2)
        self.annotation_comparison_figure.visualize(0, 0, 0, view.contour_names[0])
        self.annotation_comparison_canvas.mpl_connect('key_press_event', self.annotation_comparison_figure.keyPressEvent)
        self.annotation_comparison_canvas.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.annotation_comparison_canvas.setFocus()
        self.annotation_comparison_toolbar = NavigationToolbar(self.annotation_comparison_canvas, gui)
        layout.addWidget(self.annotation_comparison_canvas,  11,0, 1,10)
        layout.addWidget(self.annotation_comparison_toolbar, 12,0, 1,10)
        
        self.setLayout(layout)
        layout.setRowStretch(11, 3)

        
    def recalculate_figure(self):
        cont_name = self.combobox_select_contour.currentText()
        if cont_name=='Choose a Contour': return
        try:
            p1, p2 = self.annotation_comparison_figure.p1, self.annotation_comparison_figure.p2
            d = self.annotation_comparison_figure.slice_nr
            if self.annotation_comparison_figure.clinical_phases and cont_name!=self.annotation_comparison_figure.contour_name:
                phase_classes = sorted(list(self.view.clinical_phases[cont_name]))
                self.annotation_comparison_figure.clinical_p = phase_classes[0]
                
            self.annotation_comparison_figure.visualize(d, p1, p2, cont_name)
        except Exception as e: print(traceback.format_exc())
        
        
    def recalculate_metrics_table(self):
        #calculate(self, view, contname, p1, p2, eval1, eval2, pretty=True):
        cont_name = self.combobox_select_contour.currentText()
        if cont_name=='Choose a Contour': return
        try:
            p1, p2 = self.annotation_comparison_figure.p1, self.annotation_comparison_figure.p2
            self.metrics_table.calculate(self.view, cont_name, p1, p2, self.eval1, self.eval2)
            self.metrics_TableView.setModel(self.metrics_table.to_pyqt5_table_model())
            self.metrics_TableView.resizeColumnsToContents()
            self.contourname_lbl.setText('Contour: '+cont_name)
            self.phases_lbl.setText('Phases: '+str(p1)+', '+str(p2))
            if p1!=p2: self.equalphases_lbl.setText('!! Attention !! Unequal Phases')
        except Exception as e: print(traceback.format_exc())
        
        
        
        