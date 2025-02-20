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

from Lumos.Tables import *
from Lumos.Metrics import *
from Lumos import utils
from Lumos.Figures.Visualization import *

from Lumos.utils import findMainWindow, findCCsOverviewTab, PolygonPatch


class LGE_Multi_Reader_Comparison(Visualization):
    def set_view(self, view):     self.view   = view
    def set_canvas(self, canvas): self.canvas = canvas
    def set_gui(self, gui):       self.gui    = gui

    def set_values(self, view, canvas, eval_dict): 
        """
        view (LazyLuna.Views.View): a view for the analysis (needs to be LGE sax)
        canvas (FigureCanvas):      canvas associated with figure
        eval_dict (dict):           dictionary of all evaluations eval1, eval2, ... for number of task and one case
        """
        self.view            = view
        self.canvas          = canvas
        self.p               = 0
        self.eval_dict       = eval_dict
        self.add_annotation  = True
        self.cmap            = 'gray'
        self.dcm_tags        = False
        self.info            = True
        self.zoom            = False
        self.clinical_phases = False
        self.clinical_p      = None
        
    
        
    def visualize(self, slice_nr, eval_dict, contour_name, debug=False):                                                                                         
        """Takes a multicomparison for one case and displays the image with annos and histograms side by side
        
        Note:
            requires setting values first:
            - self.set_view(View)
            - self.set_canvas(canvas)
            - self.set_gui(gui)
        
        Args:
            slice_nr (int):     number of the slice that is being displayed
            eval_dict (dict):   dictionary of all evaluations eval1, eval2, ... for number of task and one case
            contour_name (str): name of the annotation (e.g. 'lv_myo', 'lv_scar', ...)
            debug (bool):       gives time if True 
        """
        
        # Histograms
        colors = ['green', 'grey']
        dcm    = self.eval_dict[0].get_dcm(slice_nr, 0)
        img , anno = dict(), dict()
        weights_dict, values_dict = dict(), dict()
        thresh_dict = dict()
        for i in eval_dict.keys(): #i = number of tasks
            img[i], anno[i] = self.eval_dict[i].get_img_anno(slice_nr, 0)
            geo_myo         = anno[i].get_contour('lv_myo')
            mask_myo        = utils.to_mask_pct(geo_myo, dcm.Columns, dcm.Rows)
            
            #scar if rausgenommen
            # for scar show scar plus exclusions
            #if contour_name == 'lv_scar':
            #    geo_scar    = anno[i].get_contour('lv_scar')
            #    geo_ex      = anno[i].get_contour('lge_ex')
            #    mask_scar_helper    = utils.to_mask_pct(geo_scar, dcm.Columns, dcm.Rows)
            #    mask_lge_ex_helper  = utils.to_mask_pct(geo_ex, dcm.Columns, dcm.Rows)
            #    mask_scar           = mask_scar_helper + mask_lge_ex_helper
            #else:
            geo_scar    = anno[i].get_contour(contour_name)
            mask_scar   = utils.to_mask_pct(geo_scar, dcm.Columns, dcm.Rows)
            
            myo_array  = np.where(mask_myo!=0, img[i], 0)
            scar_array = np.where(mask_scar!=0, img[i], 0)
            
            healthy_myo_array = np.where(scar_array==0, myo_array, 0)
            
            healthy_myo_array_wo_zeros = healthy_myo_array[np.where(healthy_myo_array!=0)]
            scar_array_wo_zeros        = scar_array[np.where(scar_array!=0)]
            
            weights    = [np.ravel(mask_scar[np.where(scar_array!=0)]), np.ravel(mask_myo[np.where(healthy_myo_array!=0)])]
            values     = [np.ravel(scar_array_wo_zeros), np.ravel(healthy_myo_array_wo_zeros)]

            weights_dict[i] = weights
            values_dict[i]  = values
            # collect thresholds for slices
            try:
                thresh_dict[i] = { slice_nr : self.eval_dict[i].get_threshold(slice_nr, 0, string=True) }
            except:
                thresh_dict[i] = { slice_nr : np.nan }

        
        if debug: print('Start'); st = time()
        self.clear()
        self.slice_nr, self.p, self.contour_name = slice_nr, 0, contour_name
        
        spec      = gridspec.GridSpec(nrows=len(eval_dict.keys()), ncols=2, figure=self, hspace=0.2, width_ratios= [1,2])
        for i in eval_dict.keys():
            vmin, vmax  = (min(np.min(img[i]) for i in eval_dict.keys()), max(np.max(img[i]) for i in eval_dict.keys())) if self.cmap=='gray' else self.view.cmap_vlims
            h, w        = img[0].shape
            extent_row1 =(0, w, h, 0)
            if i ==0:
                self.ax1  = self.add_subplot(spec[i,0])
                self.ax1.set_xticks([]) 
                self.ax1.set_yticks([])
                self.ax2  = self.add_subplot(spec[i,1])
                self.ax1.imshow(img[i], self.cmap, extent=extent_row1, vmin=vmin, vmax=vmax)
                self.ax2.hist(values_dict[i], bins = 200, weights = weights_dict[i], stacked = True, color = colors)

                #threshline 
                self.ax2.axvline(np.floor(self.eval_dict[i].get_threshold(slice_nr, 0)), color = 'darkred')
                #thresh=self.eval_dict[i].get_threshold(slice_nr, 0, string=True)
                #ymin, ymax = self.ax2.get_ybound()
                #self.ax2.plot([thresh, thresh], [ymin, ymax], color = 'tab:green')
                
                if self.add_annotation:
                    if self.cmap=='gray':
                        anno[i].plot_face     (self.ax1, contour_name, alpha=0.4, c='green')
                    else:
                        anno[i].plot_contours (self.ax1, contour_name, c='w')
                    #anno[i].plot_points(self.ax1)       #sax ref 
                d = shapely.geometry.Polygon([[0,0],[1,1],[1,0]])
                if self.cmap=='gray': patches = [PolygonPatch(d, c=c, alpha=0.4) for c in ['green']]
                else:                 patches = [PolygonPatch(d, c=c, alpha=1.0) for c in ['green']]
                handles = [self.eval_dict[i].taskname]
                self.ax1.legend(patches, handles)
                #if contour_name == 'lv_scar':
                patch_green  = [PolygonPatch(d, c=c, alpha=0.4) for c in ['green']]
                handle_green = [self.eval_dict[i].taskname+': '+  contour_name]
                
                self.ax2.legend(patch_green, handle_green)
                if self.info:
                    xmin, xmax, ymin, ymax = self.ax2.axis()
                    xx, yy   = (self.xlims[0] if self.zoom else 2), (self.ylims[0]+3 if self.zoom else 0)
                    xx1, yy1 = xmin, ymax
                    s  = 'Slice: ' + str(slice_nr) + '\nPhase: ' + str(0)
                    t = dict()
                    
                    t[i] = 'Threshold: ' + str(self.eval_dict[i].get_threshold(slice_nr, 0, string=True))
                    self.ax1.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                                  horizontalalignment='left', verticalalignment='top')
                    if contour_name == 'lv_scar': 
                        self.ax2.text(x=xx1, y=yy1, s=t[0], c='w', fontsize=8, bbox=dict(facecolor='k'), 
                             horizontalalignment='left', verticalalignment='top')
               
            
            else:
                self.ax3   = self.add_subplot(spec[i,0], sharex=self.ax1, sharey=self.ax1)
                self.ax3.set_xticks([]) 
                self.ax3.set_yticks([])
                self.ax4   = self.add_subplot(spec[i,1], sharex=self.ax2, sharey=self.ax2)
                self.ax3.imshow(img[i], self.cmap, extent=extent_row1, vmin=vmin, vmax=vmax)
                self.ax4.hist(values_dict[i], bins = 200, weights = weights_dict[i], stacked = True, color = colors)
                self.ax4.axvline(np.floor(self.eval_dict[i].get_threshold(slice_nr, 0)), color = 'darkred')
                if self.add_annotation:
                    if self.cmap=='gray':
                        anno[i].plot_face     (self.ax3, contour_name, alpha=0.4, c='green')
                    else:
                        anno[i].plot_contours (self.ax3, contour_name, c='w')
                    #anno[i].plot_points(self.ax3)        #sax ref
                d = shapely.geometry.Polygon([[0,0],[1,1],[1,0]])
                if self.cmap=='gray': patches = [PolygonPatch(d, c=c, alpha=0.4) for c in ['green']]
                else:                 patches = [PolygonPatch(d, c=c, alpha=1.0) for c in ['green']]
                handles = [self.eval_dict[i].taskname]
                self.ax3.legend(patches, handles)
                patch_green  = [PolygonPatch(d, c=c, alpha=0.4) for c in ['green']]
                handle_green = [self.eval_dict[i].taskname+': '+  contour_name]
                
                self.ax4.legend(patch_green, handle_green)
                if self.info:
                    xmin, xmax, ymin, ymax = self.ax2.axis()
                    xx, yy = (self.xlims[0] if self.zoom else 2), (self.ylims[0]+3 if self.zoom else 0)
                    xx1, yy1 = xmin, ymax
                    s  = 'Slice: ' + str(slice_nr) + '\nPhase: ' + str(0)
                    t = dict() #ok das hier zu definieren oder raus aus schleife?
                    t[i] = 'Threshold: ' + str(self.eval_dict[i].get_threshold(slice_nr, 0, string=True))
                    
                    self.ax3.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                                  horizontalalignment='left', verticalalignment='top')
                    if contour_name == 'lv_scar':
                        self.ax4.text(x=xx1, y=yy1, s=t[i], c='w', fontsize=8, bbox=dict(facecolor='k'), 
                                     horizontalalignment='left', verticalalignment='top')
                
       
        
        if self.zoom: 
            for ax in [self.ax1, self.ax3]: 
                ax.set_xlim(self.xlims); ax.set_ylim(self.ylims); ax.invert_yaxis()
        
        
        if self.dcm_tags:
            dcm = self.eval_dict[0].get_dcm(slice_nr, 0)
            xx, yy = (self.xlims[1] if self.zoom else w-2), (self.ylims[1]-3 if self.zoom else h)
            s  = 'Series Descr.:   ' + dcm.SeriesDescription+'\n'
            s += 'Slice Thickness: ' + f"{dcm.SliceThickness:.2f}"+'\n'
            s += 'Slice Position:  ' + f"{dcm.SliceLocation:.2f}"+'\n'
            s += 'Pixel Size:      ' + str([float(f"{ps:.2f}") for ps in dcm.PixelSpacing])
            self.ax1.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k', edgecolor='w', linewidth=1),
                          horizontalalignment='right', verticalalignment='bottom')
        '''
        if self.clinical_phases:
            if p1!=p2:
                xx, yy = (self.xlims[0] if self.zoom else 2), (self.ylims[0]+3 if self.zoom else 0)
                s = 'Attention, unequal phases'
                self.ax2.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                              horizontalalignment='left', verticalalignment='top')
        '''


        
        def onclick(event):
            if event.dblclick:
                try:
                    overviewtab = findCCsMultiOverviewTab()
                    overviewtab.open_title_and_comments_popup(self, fig_name=self.eval_dict[0].name+', slice: ' + str(slice_nr) + ' annotation comparison')
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
        self.canvas.draw()
        self.canvas.flush_events()

        if debug: print('Took: ', time()-st)
        
    
    def keyPressEvent(self, event):
        eval_dict = self.eval_dict
        slice_nr, p, contour_name = self.slice_nr, 0, self.contour_name
        if event.key == 'shift': self.add_annotation = not self.add_annotation
        if event.key == 'z'    : self.set_zoom()
        if event.key == 'up'   : slice_nr = (slice_nr-1) % eval_dict[0].nr_slices
        if event.key == 'down' : slice_nr = (slice_nr+1) % eval_dict[0].nr_slices
        #if not self.clinical_phases:
        #    if event.key == 'left' : p1 = p2 = (p1-1) % eval1.nr_phases
        #    if event.key == 'right': p1 = p2 = (p1+1) % eval1.nr_phases
        #else:
        #    phase_classes = sorted(list(self.view.clinical_phases[self.contour_name]))
        #    idx = phase_classes.index(self.clinical_p)
        #    if event.key == 'left' : self.clinical_p = phase_classes[(idx-1) % len(phase_classes)]
        #    if event.key == 'right': self.clinical_p = phase_classes[(idx+1) % len(phase_classes)]
            #for i in eval_dict.keys():    
            #    p = eval_dict[i].clinical_parameters[self.clinical_p][0]
            #p2 = eval2.clinical_parameters[self.clinical_p][0]
        self.visualize(slice_nr, eval_dict, contour_name)
        
    def select_cmap(self):
        if self.cmap != 'gray': self.cmap = 'gray'
        else:                   self.cmap = self.view.cmap
        self.visualize(self.slice_nr, self.eval_dict, self.contour_name)
        
    def present_dicom_tags(self):
        self.dcm_tags = not self.dcm_tags
        self.visualize(self.slice_nr, self.eval_dict, self.contour_name)
        
    def set_zoom(self):
        self.zoom = not self.zoom
        if not self.zoom: self.visualize(self.slice_nr, self.eval_dict, self.contour_name); return
        bounds = np.asarray([self.eval_dict[i].bounding_box for i in self.eval_dict.keys()])
        xmin, _, ymin, _ = np.min(bounds, axis=0); _, xmax, _, ymax = np.max(bounds, axis=0)
        h, w = self.eval_dict[0].get_img(0, 0).shape
        self.xlims, self.ylims = (max(xmin-10,0), min(xmax+10,w)), (max(ymin-10,0), min(ymax+10,h))
        self.visualize(self.slice_nr, self.eval_dict, self.contour_name)

    def set_phase_choice(self):
        if not hasattr(self.view, 'clinical_phases'): return
        self.clinical_phases = not self.clinical_phases
        if self.clinical_phases:
            phase_classes = sorted(list(self.view.clinical_phases[self.contour_name]))
            self.clinical_p = phase_classes[0]
            #p1, p2 = self.eval1.clinical_parameters[self.clinical_p][0], self.eval2.clinical_parameters[self.clinical_p][0]
        else: p1 = p2 = 0 
        self.visualize(self.slice_nr, self.eval_dict, self.contour_name)
    
    

