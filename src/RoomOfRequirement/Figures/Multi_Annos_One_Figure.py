import os
import traceback

from matplotlib import gridspec, colors, cm
from matplotlib.figure import Figure
from matplotlib.collections import PathCollection
from mpl_interactions import ioff, panhandler, zoom_factory
import matplotlib.pyplot as plt
import seaborn as sns

import shapely
from shapely.geometry import Polygon
from scipy.stats import probplot
import numpy as np
import pandas

from RoomOfRequirement.Tables import *
from RoomOfRequirement.Metrics import *
from RoomOfRequirement import utils
from RoomOfRequirement.Figures.Visualization import *

from RoomOfRequirement.utils import findMainWindow, findCCsOverviewTab, PolygonPatch


class Multi_Annos_in_One(Visualization):
    def set_view(self, view):     self.view   = view
    def set_canvas(self, canvas): self.canvas = canvas
    def set_gui(self, gui):       self.gui    = gui

    def set_values(self, view, canvas, eval_dict): 
        """
        eval_dict : Dictionary aller evaluations eval1, eval2, ... 
        """
        self.view            = view
        self.canvas          = canvas
        self.p               = dict()
        self.eval_dict       = eval_dict
        self.checked_boxes_index = list()
        self.add_annotation  = True
        self.cmap            = 'gray'
        self.dcm_tags        = False
        self.info            = True
        self.zoom            = False
        self.clinical_phases = False
        self.clinical_p      = None
        
       
    def visualize(self, slice_nr, p, eval_dict, checked_boxes_index, contour_name, debug=False):                                                                                         
        """Takes a case_comparison and presents the annotations of both readers side by side
        
        Note:
            requires setting values first:
            - self.set_view(View)
            - self.set_canvas(canvas)
            - self.set_gui(gui)
        
        Args:
            case_comparisons (list of Case_Comparison): list of case comparisons to calculate the bland altman for
            cr_name (str): the name of the Clinical Result
        """
        self.eval_dict           = eval_dict
        self.checked_boxes_index = checked_boxes_index
        ##print(eval_dict)
        #print(self.eval_dict)
        #print((checked_boxes_index))
        
        #print(eval_dict)
        colors     = {0: 'yellow', 1: 'red', 2: 'blue', 3: 'green', 4: 'magenta', 5: 'indigo', 6: 'darkorange', 7: 'c', 8: 'darkred', 9: 'tab:purple', 10: 'deepskyblue', 11: 'olive', 12: 'yellowgreen', 13: 'peru', 14: 'tan', 15: 'mediumvioletred', 16: 'lemonchiffon', 17: 'aquamarine', 18: 'rosybrown', 19: 'springgreen'}
        #for i in eval_dict.keys():
        #    dcm        = self.eval_dict[i].get_dcm(slice_nr, p[i])
        #    img        = self.eval_dict[i].get_img(slice_nr, p[i])
        dcm        = self.eval_dict[0].get_dcm(slice_nr, p[0])
        img        = self.eval_dict[0].get_img(slice_nr, p[0])
        
        anno = dict()

        for i in checked_boxes_index: #i = task number
            anno[i] = self.eval_dict[i].get_anno(slice_nr, p[i])
        #print(anno)
        if debug: print('Start'); st = time()
        self.clear()
        self.slice_nr, self.p, self.contour_name = slice_nr, p, contour_name
        #i = len(eval_dict.keys())
        spec      = gridspec.GridSpec(nrows=1, ncols=1, figure=self, hspace=0.05)
        
        h, w        = img.shape
        extent_row1 =(0, w, h, 0)
        
        self.ax1  = self.add_subplot(spec[0,0])
        self.ax1.set_xticks([]) 
        self.ax1.set_yticks([])
        self.ax1.imshow(img, self.cmap, extent=extent_row1)
        if self.add_annotation:
            for i in anno.keys():
                if self.cmap=='gray':
                    anno[i].plot_face     (self.ax1, contour_name, alpha=0.4, c=colors[i] )    
                else:
                    anno[i].plot_contours (self.ax1, contour_name, c='w')
                #anno[i].plot_points(self.ax1)             #sax ref point?
        d = shapely.geometry.Polygon([[0,0],[1,1],[1,0]])
        if self.cmap=='gray': patches = [PolygonPatch(d, c=colors[i], alpha=0.4) for i in anno.keys()]
        else:                 patches = [PolygonPatch(d, c=colors[i], alpha=1.0) for i in anno.keys()]
        handles = list()
        for i in anno.keys():
            handles.append(self.eval_dict[i].taskname)
        self.ax1.legend(patches, handles)
            
        if self.info:
            xmin, xmax, ymin, ymax = self.ax1.axis()
            xx, yy = (self.xlims[0] if self.zoom else 2), (self.ylims[0]+3 if self.zoom else 0)
            xx1, yy1 = xmin, ymax
            if not self.clinical_phases:
                s  = 'Slice: ' + str(slice_nr) + '\nPhase: ' + str(p[0])
                self.ax1.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                          horizontalalignment='left', verticalalignment='top')
            
        if self.zoom: 
            for ax in [self.ax1]: 
                ax.set_xlim(self.xlims); ax.set_ylim(self.ylims); ax.invert_yaxis()
        
        
        if self.dcm_tags:
            #for i in eval_dict.keys():
            dcm        = self.eval_dict[0].get_dcm(slice_nr, p[0])
            xx, yy = (self.xlims[1] if self.zoom else w-2), (self.ylims[1]-3 if self.zoom else h)
            s  = 'Series Descr.:   ' + dcm.SeriesDescription+'\n'
            s += 'Slice Thickness: ' + f"{dcm.SliceThickness:.2f}"+'\n'
            s += 'Slice Position:  ' + f"{dcm.SliceLocation:.2f}"+'\n'
            s += 'Pixel Size:      ' + str([float(f"{ps:.2f}") for ps in dcm.PixelSpacing])
            self.ax1.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k', edgecolor='w', linewidth=1),
                          horizontalalignment='right', verticalalignment='bottom')
        
        if self.clinical_phases:
            if (p[0]!=p[i] for i in eval_dict.keys()):
                xx, yy = (self.xlims[0] if self.zoom else 2), (self.ylims[0]+3 if self.zoom else 0)
                s = 'Attention, unequal phases'
                self.ax1.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                              horizontalalignment='left', verticalalignment='top')
        
        def onclick(event):
            #for i in eval_dict.keys():
            name_case        = self.eval_dict[0].name
            if event.dblclick:
                try:
                    overviewtab = findCCsMultiOverviewTab()
                    overviewtab.open_title_and_comments_popup(self, fig_name=name_case+', slice: ' + str(slice_nr) + ' annotation comparison')
                except: print(traceback.format_exc()); pass
            if event.button == 3: # right click
                try:
                    if not hasattr(self,'menu'):
                        from PyQt6.QtGui import QCursor
                        from PyQt6 import QtWidgets
                        pos = QCursor.pos()
                        self.menu = QtWidgets.QMenu()
                        self.menu.addAction("Show Dicom Tags", self.present_dicom_tags)
                        self.menu.addAction("Zoom", self.set_zoom)
                        self.menu.addSeparator()
                        self.menu.addAction("Select Colormap", self.select_cmap)
                        self.menu.addAction("Clinical Phases", self.set_phase_choice)
                        self.menu.move(pos)
                    self.menu.show()
                except: print(traceback.format_exc()); pass
                
        
        self.canvas.mpl_connect('button_press_event', onclick)
        self.patch.set_facecolor('white')
        self.subplots_adjust(top=0.98, bottom=0.02, left=0.02, right=0.98, wspace=0.005)
        #self.subplots_adjust(top=1, bottom=0, left=0, right=1, wspace=0.005)
        self.canvas.draw()
        self.canvas.flush_events()

        if debug: print('Took: ', time()-st)
        
    
    def keyPressEvent(self, event):
        eval_dict = self.eval_dict
        checked_boxes_index = self.checked_boxes_index
        #help_list = list()
        ##for j in eval_dict.keys():
        #    help_list.append(j)
        #j = help_list[0]
        #j = checked_boxes_index[0]
        #print(j)
        slice_nr, p, contour_name = self.slice_nr, self.p, self.contour_name
        if event.key == 'shift': self.add_annotation = not self.add_annotation
        if event.key == 'z'    : self.set_zoom()
        if event.key == 'up'   : slice_nr = (slice_nr-1) % eval_dict[0].nr_slices
        if event.key == 'down' : slice_nr = (slice_nr+1) % eval_dict[0].nr_slices
        
        
        if not self.clinical_phases:
            print('not clinical phases')
            if event.key == 'left' :
                print('left')
                print('p0 before changed', p[0])
                if 0 not in checked_boxes_index: 
                    p[0] = (p[0]-1) % eval_dict[0].nr_phases
                    print('index len', len(checked_boxes_index))
                    print('p0 after changed for len==0', p[0])
                #if len(checked_boxes_index) ==0: 
                #    p[0] = (p[0]-1) % eval_dict[0].nr_phases
                #    print('index len', len(checked_boxes_index))
                #    print('p0 after changed for len==0', p[0])
                for i in checked_boxes_index:
                    p[i] = (p[i]-1) % eval_dict[i].nr_phases
                    print('i, p i', i, p[i])
                #if len(checked_boxes_index) ==0: p[0] = (p[0]-1) % eval_dict[0].nr_phases 
            if event.key == 'right': 
                print('right')
                print('p0 before changed', p[0])
                if 0 not in checked_boxes_index: 
                #if len(checked_boxes_index) ==0: 
                    p[0] = (p[0]+1) % eval_dict[0].nr_phases
                    print('index len', len(checked_boxes_index))
                    print('p0 after changed', p[0])
                for i in checked_boxes_index:
                    p[i] = (p[i]+1) % eval_dict[i].nr_phases 
                    print('i, p i',i, p[i])
                #if len(checked_boxes_index) ==0: p[0] = (p[0]+1) % eval_dict[0].nr_phases
        else:
            phase_classes = sorted(list(self.view.clinical_phases[self.contour_name]))
            idx = phase_classes.index(self.clinical_p)
            print('idx', idx)
            print(self.clinical_p)
            if event.key == 'left' : self.clinical_p = phase_classes[(idx-1) % len(phase_classes)]
            if event.key == 'right': self.clinical_p = phase_classes[(idx+1) % len(phase_classes)]
            for i in checked_boxes_index:    
                p[i] = eval_dict[i].clinical_parameters[self.clinical_p][0]
            #p2 = eval2.clinical_parameters[self.clinical_p][0]
        self.visualize(slice_nr, p, eval_dict, checked_boxes_index, contour_name)
        
    def select_cmap(self):
        if self.cmap != 'gray': self.cmap = 'gray'
        else:                   self.cmap = self.view.cmap
        self.visualize(self.slice_nr, self.p, self.eval_dict, self.checked_boxes_index, self.contour_name)
        
    def present_dicom_tags(self):
        self.dcm_tags = not self.dcm_tags
        self.visualize(self.slice_nr, self.p, self.eval_dict, self.checked_boxes_index, self.contour_name)
        
    def set_zoom(self):
        self.zoom = not self.zoom
        if not self.zoom: self.visualize(self.slice_nr, self.p, self.eval_dict, self.checked_boxes_index, self.contour_name); return
        bounds = np.asarray([self.eval_dict[i].bounding_box for i in self.eval_dict.keys()])
        xmin, _, ymin, _ = np.min(bounds, axis=0); _, xmax, _, ymax = np.max(bounds, axis=0)
        #for i in self.eval_dict.keys():
        img = self.eval_dict[0].get_img(0, 0)
        h, w = img.shape
        self.xlims, self.ylims = (max(xmin-10,0), min(xmax+10,w)), (max(ymin-10,0), min(ymax+10,h))
        self.visualize(self.slice_nr, self.p, self.eval_dict, self.checked_boxes_index, self.contour_name)

    def set_phase_choice(self):
        if not hasattr(self.view, 'clinical_phases'): return
        self.clinical_phases = not self.clinical_phases
        p = self.p
        if self.clinical_phases:
            phase_classes = sorted(list(self.view.clinical_phases[self.contour_name]))
            self.clinical_p = phase_classes[0]
            for i in self.checked_boxes_index:
                p[i] = self.eval_dict[i].clinical_parameters[self.clinical_p][0]
        else:
            for i in self.checked_boxes_index:
                p[i] = 0 
        self.visualize(self.slice_nr, p, self.eval_dict, self.checked_boxes_index, self.contour_name)
    
    

