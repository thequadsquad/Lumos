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

#from RoomOfRequirement.Annotation import *           
#from RoomOfRequirement.loading_functions import *    
#from RoomOfRequirement.Evaluation import *  





class LGE_Annotation_Histo_Comparison(Visualization):
    def set_view(self, view):     self.view   = view
    def set_canvas(self, canvas): self.canvas = canvas
    def set_gui(self, gui):       self.gui    = gui

    def set_values(self, view, canvas, eval1, eval2):
        self.view              = view
        self.canvas            = canvas
        #self.p                 = 0
        self.eval1, self.eval2 = eval1, eval2

        self.add_annotation  = True
        self.cmap            = 'gray'
        self.dcm_tags        = False
        self.info            = True
        self.zoom            = False
        self.clinical_phases = False
        self.clinical_p      = None
        
    
    
        
    def visualize(self, slice_nr, p1, p2, contour_name, debug=False):                                                                                         
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
        self.slice_nr = slice_nr
        
        colors1      = ['#785ef0', 'grey']      #red to light orange 94CBEC
        colors2      = ['#ffb000', 'grey']  #blue 000000
        dcm          = self.eval1.get_dcm(slice_nr, 0)
        img1, anno1  = self.eval1.get_img_anno(slice_nr, 0)
        img2, anno2  = self.eval2.get_img_anno(slice_nr, 0)
        geo_myo1     = anno1.get_contour(self.view.contour_names[0])
        #geo_myo1     = anno1.get_contour('lv_myo')
        mask_myo1   = utils.to_mask_pct(geo_myo1, dcm.Columns, dcm.Rows)
        
        #if contour_name == 'lv_scar':
        #    geo_scar1    = anno1.get_contour('lv_scar')
        #    geo_ex1      = anno1.get_contour('lge_ex')
        #    mask_scar1_helper  = utils.to_mask_pct(geo_scar1, dcm.Columns, dcm.Rows)
        #    mask_lge_ex_helper1  = utils.to_mask_pct(geo_ex1, dcm.Columns, dcm.Rows)
        #    mask_scar1  = mask_scar1_helper + mask_lge_ex_helper1
        #else:
        geo_scar1    = anno1.get_contour(contour_name)
        mask_scar1  = utils.to_mask_pct(geo_scar1, dcm.Columns, dcm.Rows)
        
        
        myo_array1  = np.where(mask_myo1!=0, img1, 0)
        scar_array1 = np.where(mask_scar1!=0, img1, 0)
        
        healthy_myo_array1 = np.where(scar_array1==0, myo_array1, 0)
        
        healthy_myo_array_wo_zeros1 = healthy_myo_array1[np.where(healthy_myo_array1!=0)]
        scar_array_wo_zeros1        = scar_array1[np.where(scar_array1!=0)]
        
        weights1    = [np.ravel(mask_scar1[np.where(scar_array1!=0)]), np.ravel(mask_myo1[np.where(healthy_myo_array1!=0)])]
        values1     = [np.ravel(scar_array_wo_zeros1), np.ravel(healthy_myo_array_wo_zeros1)]
        
        
        #n1, bins1, patches1 = plt.hist(values1, bins = 200, weights = weights1, stacked = True, color = colors)

        geo_myo2     = anno2.get_contour('lv_myo')
        mask_myo2   = utils.to_mask_pct(geo_myo2, dcm.Columns, dcm.Rows)
        #if contour_name == 'lv_scar':
        #    geo_scar2    = anno2.get_contour('lv_scar')
        #    geo_ex2      = anno2.get_contour('lge_ex')
        #    mask_scar2_helper  = utils.to_mask_pct(geo_scar2, dcm.Columns, dcm.Rows)
        #    mask_lge_ex_helper2  = utils.to_mask_pct(geo_ex2, dcm.Columns, dcm.Rows)
        #    mask_scar2  = mask_scar2_helper + mask_lge_ex_helper2
        #else:
        geo_scar2    = anno2.get_contour(contour_name)
        mask_scar2  = utils.to_mask_pct(geo_scar2, dcm.Columns, dcm.Rows)
    
        myo_array2  = np.where(mask_myo2!=0, img2, 0)
        scar_array2 = np.where(mask_scar2!=0, img2, 0)
        
        healthy_myo_array2 = np.where(scar_array2==0, myo_array2, 0)
        
        healthy_myo_array_wo_zeros2 = healthy_myo_array2[np.where(healthy_myo_array2!=0)]
        scar_array_wo_zeros2        = scar_array2[np.where(scar_array2!=0)]
        
        weights2    = [np.ravel(mask_scar2[np.where(scar_array2!=0)]), np.ravel(mask_myo2[np.where(healthy_myo_array2!=0)])]
        values2     = [np.ravel(scar_array_wo_zeros2), np.ravel(healthy_myo_array_wo_zeros2)]
        #n2, bins2, patches2 = plt.hist(values2, bins = 200, weights = weights2, stacked = True, color = colors)

#besser aus Tabelle nehmen? 
        try:
            thresh1 = self.eval1.get_threshold(slice_nr, p1, string=True)
            #thresh1 = min(i for i in np.ravel(scar_array1) if i > 0)
        except:
            thresh1 = np.nan  
        try:
            thresh2 = self.eval2.get_threshold(slice_nr, p2, string=True)
            #thresh2 = min(i for i in np.ravel(scar_array2) if i > 0)
        except:
            thresh2 = np.nan  

        
        if debug: print('Start'); st = time()
        self.clear()
        self.slice_nr, self.p1, self.p2, self.contour_name = slice_nr, p1, p2, contour_name
        spec = gridspec.GridSpec(nrows=2, ncols=4, figure=self, hspace=0.0)
        self.ax1  = self.add_subplot(spec[0,0])
        self.ax2  = self.add_subplot(spec[0,1], sharex=self.ax1, sharey=self.ax1)
        self.ax3  = self.add_subplot(spec[0,2], sharex=self.ax1, sharey=self.ax1)
        self.ax4  = self.add_subplot(spec[0,3], sharex=self.ax1, sharey=self.ax1)
        self.ax5  = self.add_subplot(spec[1,:-2])
        self.ax6  = self.add_subplot(spec[1,-2:], sharex=self.ax5, sharey=self.ax5)
        self.ax6.tick_params(labelleft=False)  
        h, w  = img1.shape
        extent_row1=(0, w, h, 0)
        
        vmin, vmax = (min(np.min(img1), np.min(img2)), max(np.max(img1), np.max(img2))) if self.cmap=='gray' else self.view.cmap_vlims
        self.ax1.imshow(img1, self.cmap, extent=extent_row1, vmin=vmin, vmax=vmax)
        self.ax2.imshow(img1, self.cmap, extent=extent_row1, vmin=vmin, vmax=vmax)
        self.ax3.imshow(img2, self.cmap, extent=extent_row1, vmin=vmin, vmax=vmax)
        self.ax4.imshow(img1, self.cmap, extent=extent_row1, vmin=vmin, vmax=vmax)
        
        self.ax5.hist(values1, bins = 200, weights = weights1, stacked = True, color = colors1)
        #threshline 
        self.ax5.axvline(np.floor(self.eval1.get_threshold(slice_nr, p1)), color = 'darkred')
        self.ax6.hist(values2, bins = 200, weights = weights2, stacked = True, color = colors2)
        #threshline 
        self.ax6.axvline(np.floor(self.eval2.get_threshold(slice_nr, p2)), color = 'darkred')

        if self.add_annotation:
            if self.cmap=='gray':
                anno1.plot_face           (self.ax1,        contour_name, alpha=0.4, c='#785ef0')  #r
                anno1.plot_cont_comparison(self.ax2, anno2, contour_name, alpha=0.4)
                anno2.plot_face           (self.ax3,        contour_name, alpha=0.4, c='#ffb000')  #b
            else:
                anno1.plot_contours       (self.ax1,        contour_name, c='w')
                anno1.plot_cont_comparison(self.ax2, anno2, contour_name, colors=['g','white','black'], alpha=1.0)
                anno2.plot_contours       (self.ax3,        contour_name, c='k')
            anno1.plot_points(self.ax1)
            anno2.plot_points(self.ax3)
        for ax in [self.ax1, self.ax2, self.ax3]: ax.set_xticks([]); ax.set_yticks([])
        
        d = shapely.geometry.Polygon([[0,0],[1,1],[1,0]])
        if self.cmap=='gray': patches = [PolygonPatch(d, c=c, alpha=0.4) for c in ['#785ef0', '#dc267f', '#ffb000']]   #['red', 'green', 'blue']
        else:                 patches = [PolygonPatch(d, c=c, alpha=1.0) for c in ['white', 'green', 'black']]
        handles = [self.eval1.taskname, self.eval1.taskname+' & '+self.eval2.taskname, self.eval2.taskname]
        self.ax4.legend(patches, handles)
        #if contour_name == 'lv_scar':
        patch_red  = [PolygonPatch(d, c=c, alpha=0.4) for c in ['#785ef0']] #red
        patch_blue = [PolygonPatch(d, c=c, alpha=0.4) for c in ['#ffb000']] #blue
        handle_red = [self.eval1.taskname+': '+  contour_name]
        handle_blue= [self.eval2.taskname+': '+  contour_name]
        self.ax5.legend(patch_red, handle_red)
        self.ax6.legend(patch_blue, handle_blue)
        
        
        if self.zoom: 
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]: 
                ax.set_xlim(self.xlims); ax.set_ylim(self.ylims); ax.invert_yaxis()
        
        if self.info:
            xmin, xmax, ymin, ymax = self.ax5.axis()
            xx, yy = (self.xlims[0] if self.zoom else 2), (self.ylims[0]+3 if self.zoom else 0)
            xx1, yy1 = xmin, ymax
            s  = 'Slice: ' + str(slice_nr) + '\nPhase: ' + str(p1)
            t1 = 'Threshold: ' + str(thresh1)
            t2 = 'Threshold: ' + str(thresh2)
            self.ax1.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                          horizontalalignment='left', verticalalignment='top')
            s  = 'Slice: ' + str(slice_nr) + '\nPhase: ' + str(p2)
            self.ax3.text(x=xx, y=yy, s=s, c='w', fontsize=8, bbox=dict(facecolor='k'),
                          horizontalalignment='left', verticalalignment='top')
            if contour_name == 'lv_scar':
                self.ax5.text(x=xx1, y=yy1, s=t1, c='w', fontsize=8, bbox=dict(facecolor='k'), 
                             horizontalalignment='left', verticalalignment='top')
                self.ax6.text(x=xx1, y=yy1, s=t2, c='w', fontsize=8, bbox=dict(facecolor='k'), 
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
        self.patch.set_facecolor('white')
        self.subplots_adjust(top=1, bottom=0.1, left=0.05, right=0.95, wspace=0.005)
        #self.subplots_adjust(top=1, bottom=0, left=0, right=1, wspace=0.005)
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
            p1, p2 = self.eval1.clinical_parameters[self.clinical_p][0], self.eval2.clinical_parameters[self.clinical_p][0]
        else: p1 = p2 = 0 
        self.visualize(self.slice_nr, p1, p2, self.contour_name)
    






























'''    

    def keyPressEvent(self, event):
        eval1, eval2 = self.eval1, self.eval2
        slice_nr     = self.slice_nr
        #if event.key == 'shift': self.add_annotation = not self.add_annotation
        #if event.key == 'z'    : self.set_zoom()
        if event.key == 'up'   : slice_nr = (slice_nr-1) % eval1.nr_slices
        if event.key == 'down' : slice_nr = (slice_nr+1) % eval1.nr_slices
        #if not self.clinical_phases:
        #    if event.key == 'left' : p1 = p2 = (p1-1) % eval1.nr_phases
        #    if event.key == 'right': p1 = p2 = (p1+1) % eval1.nr_phases
        #else:
        #    phase_classes = sorted(list(self.view.clinical_phases[self.contour_name]))
        #    idx = phase_classes.index(self.clinical_p)
        #    if event.key == 'left' : self.clinical_p = phase_classes[(idx-1) % len(phase_classes)]
        #    if event.key == 'right': self.clinical_p = phase_classes[(idx+1) % len(phase_classes)]
        #    p1 = eval1.clinical_parameters[self.clinical_p][0]
        #    p2 = eval2.clinical_parameters[self.clinical_p][0]
        self.visualize(slice_nr)
############################################
#ANPASSEN!!!
############################################


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
            p1, p2 = self.eval1.clinical_parameters[self.clinical_p][0], self.eval2.clinical_parameters[self.clinical_p][0]
        else: p1 = p2 = 0 
        self.visualize(self.slice_nr, p1, p2, self.contour_name)
    
    def store(self, storepath, figurename='_annotation_comparison.png'):
        self.tight_layout()
        now = str(datetime.now()).replace('-','_').replace(' ','_').replace(':','_').split('.')[0]
        figname = self.eval1.name+'_slice_' + str(self.slice_nr)+'_'+now+'_'+figurename
        self.savefig(os.path.join(storepath, figname), dpi=300, facecolor="#000000")
        return os.path.join(storepath, figname)
    
























        self.clf()                                                                             #classifier?
        ax = self.add_subplot(111, position=[0.16, 0.16, 0.68, 0.68])
        swarm_palette   = sns.color_palette(["#061C36", "#061C36"])                            #sns = seaborn
        
        rows = []
        self.failed_cr_rows = []
        for eval1, eval2 in zip(evals1, evals2):
            cr1, cr2 = cr.get_val(eval1), cr.get_val(eval2)
            if np.isnan(cr1) or np.isnan(cr2): self.failed_cr_rows.append([eval1.name, eval1.studyuid])
            else: rows.append([eval1.name, eval1.studyuid, (cr1+cr2)/2.0, cr1-cr2])
        df = DataFrame(rows, columns=['case_name', 'studyuid', cr_name, cr_name+' difference'])
        sns.scatterplot(ax=ax, x=cr_name, y=cr_name+' difference', data=df, markers='o', 
                        palette=swarm_palette, size=np.abs(df[cr_name+' difference']), s=10, legend=False)
        ax.axhline(df[cr_name+' difference'].mean(), ls="-", c=".2")
        ax.axhline(df[cr_name+' difference'].mean()+1.96*df[cr_name+' difference'].std(), ls=":", c=".2")
        ax.axhline(df[cr_name+' difference'].mean()-1.96*df[cr_name+' difference'].std(), ls=":", c=".2")
        ax.set_title(cr_name+' Bland Altman', fontsize=14)
        ax.set_ylabel(cr.unit, fontsize=12)
        ax.set_xlabel(cr.unit, fontsize=12)
        ax.set_xlabel(cr.name+' '+cr.unit, fontsize=12)
        sns.despine()
        texts = df['case_name'].tolist()
        studyuids = df['studyuid'].tolist()
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points", 
                            bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
        
        if not hasattr(self, 'canvas'): return
        def update_annot(ind):
            pos = ax.collections[0].get_offsets()[ind["ind"][0]]
            annot.xy = pos
            annot.set_text(texts[ind['ind'][0]])
        
        def hover(event):                                                                   #annotations werden sichtbar für hover, nur sinnvoll wenn ich auch annotations ins histo packe (vllt thresh?)
            vis = annot.get_visible()
            if event.inaxes==ax:
                cont, ind = ax.collections[0].contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    self.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        self.canvas.draw_idle()
        
        def onclick(event):                                                                 #für was will ich klicken hinzufügen? Macht das sinn für histos?
            vis = annot.get_visible()
            if event.inaxes==ax:
                try:
                    cont, ind = ax.collections[0].contains(event)
                    name = texts[ind['ind'][0]]
                    studyuid = studyuids[ind['ind'][0]]
                    eval1 = [eva for eva in evals1 if eva.studyuid==studyuid][0]
                    eval2 = [eva for eva in evals2 if eva.studyuid==studyuid][0]
                    for tab_name, tab in self.view.case_tabs.items():
                        try:
                            t = tab()
                            t.make_tab(self.gui, self.view, eval1, eval2)
                            self.gui.tabs.addTab(t, tab_name+': '+eval1.name)
                        except: print(traceback.format_exc()); pass
                except: pass
            if event.dblclick:
                try:
                    overviewtab = findCCsOverviewTab()
                    overviewtab.open_title_and_comments_popup(self, fig_name=self.cr_name+'_bland_altman')
                except: pass

        self.canvas.mpl_connect("motion_notify_event", hover)
        self.canvas.mpl_connect('button_press_event', onclick)
        #self.tight_layout()
        self.canvas.draw()
    
    def store(self, storepath, figurename='_histo_scar_myo .png'):                                                 #slice number and patient name dazu?
        self.tight_layout()
        self.savefig(os.path.join(storepath, self.cr_name+figurename), dpi=300, facecolor="#FFFFFF")               #slice number and patient name dazu? 
        return os.path.join(storepath, self.cr_name+figurename)
    







   
def histo_scar_vs_healthy_myo(dcm, geo_myo, geo_scar):
    
    pw, ph     = dcm.PixelSpacing
    mask_myo   = utils.to_mask_pct(geo_myo, ph * dcm.columns, pw * dcm.rows)
    mask_scar  = utils.to_mask_pct(geo_scar, ph * dcm.columns, pw * dcm.rows)
    
    myo_array  = np.where(mask_myo!=0, dcm.pixel_array, 0)
    scar_array = np.where(mask_scar!=0, dcm.pixel_array, 0)
    
    healthy_myo_array = np.where(scar_array==0, myo_array, 0)
    
    healthy_myo_array_wo_zeros = healthy_myo_array[np.where(healthy_myo_array!=0)]
    scar_array_wo_zeros        = scar_array[np.where(scar_array!=0)]
    
    weights    = [np.ravel(mask_myo[np.where(healthy_myo_array!=0)]), np.ravel(mask_myo[np.where(scar_array!=0)])]
    values     = [np.ravel(healthy_myo_array_wo_zeros), np.ravel(scar_array_wo_zeros)]
    colors     = ['tab:cyan', 'tab:orange']    
    
    n, bins, patches = plt.hist(values, bins = 200, weights = weights, stacked = True, color = colors)
    #plt.savefig('histo.png', dpi = 300)
    plt.show()
'''