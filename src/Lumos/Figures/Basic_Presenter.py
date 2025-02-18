import os
import traceback
from datetime import datetime

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

from Lumos.Tables import *
from Lumos.Metrics import *
from Lumos import utils
from Lumos.Figures.Visualization import *

from Lumos.utils import findMainWindow, findCCsOverviewTab


class Basic_Presenter(Visualization):
    def set_values(self, view, canvas, eval1, eval2):
        self.eval1, self.eval2 = eval1, eval2
        self.view   = view
        self.canvas = canvas
        self.add_annotation  = True
        self.cmap            = 'gray'
        self.dcm_tags        = False
        self.info            = True
        self.zoom            = False
        self.clinical_phases = False
        self.clinical_p      = None
        self.p1, self.p2     = 0, 0
    
    def visualize(self, slice_nr, p1, p2, debug=False):
        """Takes a case_comparison and presents the annotations of both readers side by side
        
        Note:
            requires setting values first:
            - self.set_values(View, Case_Comparison, canvas)
        
        Args:
            slice_nr (int): slice depth
            p1 (int): phase of first case
            p2 (int): phase of second case
        """
        self.clear()
        self.slice_nr, self.p1, self.p2 = slice_nr, p1, p2
        spec   = gridspec.GridSpec(nrows=1, ncols=2, figure=self, hspace=0.0)
        self.ax1 = self.add_subplot(spec[0,0])
        self.ax2 = self.add_subplot(spec[0,1], sharex=self.ax1, sharey=self.ax1)
        img1, anno1 = self.eval1.get_img_anno(slice_nr, p1)
        img2, anno2 = self.eval2.get_img_anno(slice_nr, p2)
        h, w     = img1.shape
        extent   = (0, w, h, 0)
        vmin, vmax = (min(np.min(img1), np.min(img2)), max(np.max(img1), np.max(img2))) if self.cmap=='gray' else self.view.cmap_vlims
        self.ax1.imshow(img1, self.cmap, extent=extent, vmin=vmin, vmax=vmax)
        self.ax2.imshow(img2, self.cmap, extent=extent, vmin=vmin, vmax=vmax)
        if self.add_annotation:
            anno1.plot_contours(self.ax1) # looks like overlooked slices when different phases for RV and LV
            anno2.plot_contours(self.ax2)
            anno1.plot_points(self.ax1)
            anno2.plot_points(self.ax2)
        for ax in [self.ax1, self.ax2]: ax.set_xticks([]); ax.set_yticks([])
        d = shapely.geometry.Polygon([[0,0],[1,1],[1,0]])
        
        if self.zoom:
            print(self.xlims, self.ylims)
            for ax in [self.ax1, self.ax2]: ax.set_xlim(self.xlims); ax.set_ylim(self.ylims); ax.invert_yaxis()
        
        self.ax1.text(x=w//2, y=5+(self.ylims[0]-3 if self.zoom else 0), 
                      s=self.eval1.taskname, c='w', fontsize=8, bbox=dict(facecolor='k'))
        self.ax2.text(x=w//2, y=5+(self.ylims[0]-3 if self.zoom else 0), 
                      s=self.eval2.taskname, c='w', fontsize=8, bbox=dict(facecolor='k'))
        
        if self.info:
            xx, yy = (self.xlims[0] if self.zoom else 2), (self.ylims[0]+3 if self.zoom else 0)
            s  = 'Slice: ' + str(slice_nr) + '\nPhase: ' + str(p1)
            self.ax1.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                          horizontalalignment='left', verticalalignment='top')
            s  = 'Slice: ' + str(slice_nr) + '\nPhase: ' + str(p2)
            self.ax2.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                          horizontalalignment='left', verticalalignment='top')
        
        if self.dcm_tags:
            dcm = self.eval1.get_dcm(slice_nr, p1)
            xx, yy = (self.xlims[0] if self.zoom else 2), (self.ylims[1]-3 if self.zoom else h)
            s  = 'Series Descr.:   ' + dcm.SeriesDescription+'\n'
            s += 'Slice Thickness: ' + f"{dcm.SliceThickness:.2f}"+'\n'
            s += 'Slice Position:  ' + f"{dcm.SliceLocation:.2f}"+'\n'
            s += 'Pixel Size:      ' + str([float(f"{ps:.2f}") for ps in dcm.PixelSpacing])
            self.ax1.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k', edgecolor='w', linewidth=1),
                          horizontalalignment='left', verticalalignment='bottom')

        
        def onclick(event):
            if event.dblclick: # image storing ("tracing") with LL
                try:
                    overviewtab = findCCsOverviewTab()
                    overviewtab.open_title_and_comments_popup(self, fig_name=self.eval1.name+', slice: '+str(slice_nr)+' annotation comparison')
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
        self.patch.set_facecolor('black')
        self.subplots_adjust(top=1, bottom=0, wspace=0.02)
        self.canvas.draw()
        self.canvas.flush_events()
        
    def keyPressEvent(self, event):
        eval1, eval2, slice_nr, p1, p2 = self.eval1, self.eval2, self.slice_nr, self.p1, self.p2
        if event.key == 'shift': self.add_annotation = not self.add_annotation
        if event.key == 'z'    : self.set_zoom()
        if event.key == 'up'   : slice_nr = (slice_nr-1) % self.eval1.nr_slices
        if event.key == 'down' : slice_nr = (slice_nr+1) % self.eval1.nr_slices
        if not self.clinical_phases:
            if event.key == 'left' : p1 = p2 = (p1-1) % eval1.nr_phases
            if event.key == 'right': p1 = p2 = (p1+1) % eval1.nr_phases
        else:
            phase_classes = sorted(list(self.view.clinical_phases['all']))
            idx = phase_classes.index(self.clinical_p)
            if event.key == 'left' : self.clinical_p = phase_classes[(idx-1) % len(phase_classes)]
            if event.key == 'right': self.clinical_p = phase_classes[(idx+1) % len(phase_classes)]
            p1 = eval1.clinical_parameters[self.clinical_p][0]
            p2 = eval2.clinical_parameters[self.clinical_p][0]
        self.visualize(slice_nr, p1, p2)
    
    def select_cmap(self):
        if self.cmap != 'gray': self.cmap = 'gray'
        else:                   self.cmap = self.view.cmap
        self.visualize(self.slice_nr, self.p1, self.p2)
        
    def present_dicom_tags(self):
        self.dcm_tags = not self.dcm_tags
        self.visualize(self.slice_nr, self.p1, self.p2)
        
    def set_zoom(self):
        self.zoom = not self.zoom
        if not self.zoom: self.visualize(self.slice_nr, self.p1, self.p2); return
        bounds = np.asarray([self.eval1.bounding_box, self.eval2.bounding_box])
        xmin, _, ymin, _ = np.min(bounds, axis=0); _, xmax, _, ymax = np.max(bounds, axis=0)
        h, w = self.eval1.get_img(0, 0).shape
        self.xlims, self.ylims = (max(xmin-10,0), min(xmax+10,w)), (max(ymin-10,0), min(ymax+10,h))
        self.visualize(self.slice_nr, self.p1, self.p2)
        
    def set_phase_choice(self):
        if not hasattr(self.view, 'clinical_phases'): return
        self.clinical_phases = not self.clinical_phases
        if self.clinical_phases:
            phase_classes = sorted(list(self.view.clinical_phases['all']))
            self.clinical_p = phase_classes[0]
            try:    p1, p2 = self.eval1.clinical_parameters[self.clinical_p][0], self.eval2.clinical_parameters[self.clinical_p][0]
            except: p1 = p2 = 0
        else: p1 = p2 = 0 
        self.visualize(self.slice_nr, p1, p2)

    def store(self, storepath, figurename='_basic_presentation.png'):
        self.patch.set_facecolor('black')
        self.subplots_adjust(top=1, bottom=0, wspace=0.02)
        now = str(datetime.now()).replace('-','_').replace(' ','_').replace(':','_').split('.')[0]
        figname = self.eval1.name+'_slice_'+str(self.slice_nr)+'_'+now+'_'+figurename
        self.savefig(os.path.join(storepath, figname), dpi=300, facecolor="#000000")
        return os.path.join(storepath, figname)
    