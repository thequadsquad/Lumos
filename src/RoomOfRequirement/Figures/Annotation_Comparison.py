import os
import traceback
from datetime import datetime

from matplotlib import gridspec, colors, cm
from matplotlib.figure import Figure
from matplotlib.collections import PathCollection
from mpl_interactions import ioff, panhandler, zoom_factory
import matplotlib.pyplot as plt
import seaborn as sns

import matplotlib
from matplotlib.patches import PathPatch
from matplotlib.path import Path

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
    

class Annotation_Comparison(Visualization):
    def set_values(self, view, canvas, eval1, eval2):
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
        self.eval1, self.eval2 = eval1, eval2
    
    def visualize(self, slice_nr, p1, p2, contour_name, debug=False):
        """Takes a case_comparison and presents a colourful annotation comparison on their respective images
        
        Note:
            requires setting values first:
            - self.set_values(View, Case_Comparison, canvas)
        
        Args:
            slice_nr (int): slice depth
            category (LazyLuna.Categories.Category): a case's category
            contour_name (str): countour type
        """
        if debug: print('Start'); st = time()
        self.clear()
        self.slice_nr, self.p1, self.p2, self.contour_name = slice_nr, p1, p2, contour_name
        spec = gridspec.GridSpec(nrows=1, ncols=4, figure=self, hspace=0.0)
        self.ax1  = self.add_subplot(spec[0,0])
        self.ax2  = self.add_subplot(spec[0,1], sharex=self.ax1, sharey=self.ax1)
        self.ax3  = self.add_subplot(spec[0,2], sharex=self.ax1, sharey=self.ax1)
        self.ax4  = self.add_subplot(spec[0,3], sharex=self.ax1, sharey=self.ax1)
        img1, anno1  = self.eval1.get_img_anno(slice_nr, p1)
        img2, anno2  = self.eval2.get_img_anno(slice_nr, p2)
        h, w  = img1.shape
        extent=(0, w, h, 0)
        vmin, vmax = (min(np.min(img1), np.min(img2)), max(np.max(img1), np.max(img2))) if self.cmap=='gray' else self.view.cmap_vlims
        self.ax1.imshow(img1, self.cmap, extent=extent, vmin=vmin, vmax=vmax)
        self.ax2.imshow(img1, self.cmap, extent=extent, vmin=vmin, vmax=vmax)
        self.ax3.imshow(img2, self.cmap, extent=extent, vmin=vmin, vmax=vmax)
        self.ax4.imshow(img1, self.cmap, extent=extent, vmin=vmin, vmax=vmax)
        if self.add_annotation:
            if self.cmap=='gray':
                anno1.plot_face           (self.ax1,        contour_name, alpha=0.4, c='r')
                anno1.plot_cont_comparison(self.ax2, anno2, contour_name, alpha=0.4)
                anno2.plot_face           (self.ax3,        contour_name, alpha=0.4, c='b')
            else:
                anno1.plot_contours       (self.ax1,        contour_name, c='w')
                anno1.plot_cont_comparison(self.ax2, anno2, contour_name, colors=['g','white','black'], alpha=1.0)
                anno2.plot_contours       (self.ax3,        contour_name, c='k')
            anno1.plot_points(self.ax1)
            anno2.plot_points(self.ax3)
        for ax in [self.ax1, self.ax2, self.ax3]: ax.set_xticks([]); ax.set_yticks([])
        
        d = shapely.geometry.Polygon([[0,0],[1,1],[1,0]])
        if self.cmap=='gray': patches = [PolygonPatch(d, c=c, alpha=0.4) for c in ['red', 'green', 'blue']]
        else:                 patches = [PolygonPatch(d, c=c, alpha=1.0) for c in ['white', 'green', 'black']]
        handles = [self.eval1.taskname, self.eval1.taskname+' & '+self.eval2.taskname, self.eval2.taskname]
        self.ax4.legend(patches, handles)
        
        if self.zoom: 
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]: 
                ax.set_xlim(self.xlims); ax.set_ylim(self.ylims); ax.invert_yaxis()
        
        if self.info:
            xx, yy = (self.xlims[0] if self.zoom else 2), (self.ylims[0]+3 if self.zoom else 0)
            s  = 'Slice: ' + str(slice_nr) + '\nPhase: ' + str(p1)
            self.ax1.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                          horizontalalignment='left', verticalalignment='top')
            s  = 'Slice: ' + str(slice_nr) + '\nPhase: ' + str(p2)
            self.ax3.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                          horizontalalignment='left', verticalalignment='top')
        
        if self.dcm_tags:
            dcm = self.eval1.get_dcm(slice_nr, p1)
            xx, yy = (self.xlims[1] if self.zoom else w-2), (self.ylims[1]-3 if self.zoom else h)
            s  = 'Series Descr.:   ' + dcm.SeriesDescription+'\n'
            s += 'Slice Thickness: ' + f"{dcm.SliceThickness:.2f}"+'\n'
            s += 'Slice Position:  ' + f"{dcm.SliceLocation:.2f}"+'\n'
            s += 'Pixel Size:      ' + str([float(f"{ps:.2f}") for ps in dcm.PixelSpacing])
            self.ax4.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k', edgecolor='w', linewidth=1),
                          horizontalalignment='right', verticalalignment='bottom')
        
        if self.clinical_phases:
            if p1!=p2:
                xx, yy = (self.xlims[0] if self.zoom else 2), (self.ylims[0]+3 if self.zoom else 0)
                s = 'Attention, unequal phases'
                self.ax2.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                              horizontalalignment='left', verticalalignment='top')
        
        def onclick(event):
            if event.dblclick:
                try:
                    overviewtab = findCCsOverviewTab()
                    overviewtab.open_title_and_comments_popup(self, fig_name=self.eval1.name+', slice: ' + str(slice_nr) + ' annotation comparison')
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
        self.subplots_adjust(top=1, bottom=0, left=0, right=1, wspace=0.005)
        self.canvas.draw()
        self.canvas.flush_events()
        if debug: print('Took: ', time()-st)
        
    
    def keyPressEvent(self, event):
        eval1, eval2 = self.eval1, self.eval2
        slice_nr, p1, p2, contour_name = self.slice_nr, self.p1, self.p2, self.contour_name
        if event.key == 'shift': self.add_annotation = not self.add_annotation
        if event.key == 'z'    : self.set_zoom()
        if event.key == 'up'   : slice_nr = (slice_nr-1) % eval1.nr_slices
        if event.key == 'down' : slice_nr = (slice_nr+1) % eval1.nr_slices
        if not self.clinical_phases:
            if event.key == 'left' : p1 = p2 = (p1-1) % eval1.nr_phases
            if event.key == 'right': p1 = p2 = (p1+1) % eval1.nr_phases
        else:
            phase_classes = sorted(list(self.view.clinical_phases[self.contour_name]))
            idx = phase_classes.index(self.clinical_p)
            if event.key == 'left' : self.clinical_p = phase_classes[(idx-1) % len(phase_classes)]
            if event.key == 'right': self.clinical_p = phase_classes[(idx+1) % len(phase_classes)]
            p1 = eval1.clinical_parameters[self.clinical_p][0]
            p2 = eval2.clinical_parameters[self.clinical_p][0]
        self.visualize(slice_nr, p1, p2, contour_name)
        
    def select_cmap(self):
        if self.cmap != 'gray': self.cmap = 'gray'
        else:                   self.cmap = self.view.cmap
        self.visualize(self.slice_nr, self.p1, self.p2, self.contour_name)
        
    def present_dicom_tags(self):
        self.dcm_tags = not self.dcm_tags
        self.visualize(self.slice_nr, self.p1, self.p2, self.contour_name)
        
    def set_zoom(self):
        self.zoom = not self.zoom
        if not self.zoom: self.visualize(self.slice_nr, self.p1, self.p2, self.contour_name); return
        bounds = np.asarray([self.eval1.bounding_box, self.eval2.bounding_box])
        xmin, _, ymin, _ = np.min(bounds, axis=0); _, xmax, _, ymax = np.max(bounds, axis=0)
        h, w = self.eval1.get_img(0, 0).shape
        self.xlims, self.ylims = (max(xmin-10,0), min(xmax+10,w)), (max(ymin-10,0), min(ymax+10,h))
        self.visualize(self.slice_nr, self.p1, self.p2, self.contour_name)

    def set_phase_choice(self):
        if not hasattr(self.view, 'clinical_phases'): return
        self.clinical_phases = not self.clinical_phases
        if self.clinical_phases:
            phase_classes = sorted(list(self.view.clinical_phases[self.contour_name]))
            self.clinical_p = phase_classes[0]
            try:    p1, p2 = self.eval1.clinical_parameters[self.clinical_p][0], self.eval2.clinical_parameters[self.clinical_p][0]
            except: p1 = p2 = 0
        else: p1 = p2 = 0 
        self.visualize(self.slice_nr, p1, p2, self.contour_name)
    
    def store(self, storepath, figurename='_annotation_comparison.png'):
        self.tight_layout()
        now = str(datetime.now()).replace('-','_').replace(' ','_').replace(':','_').split('.')[0]
        figname = self.eval1.name+'_slice_' + str(self.slice_nr)+'_'+now+'_'+figurename
        self.savefig(os.path.join(storepath, figname), dpi=300, facecolor="#000000")
        return os.path.join(storepath, figname)
    