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

from RoomOfRequirement.utils import findMainWindow, findCCsOverviewTab

class Mapping_Slice_Average_PairedBoxplot(Visualization):
        
    def set_canvas(self, canvas):
        self.canvas = canvas
        
    def set_gui(self, gui):
        self.gui = gui
    
    def visualize(self, view, evals1, evals2):
        """Takes a list of case_comparisons and presents a paired boxplot for myocardial pixel averages per slice
        
        Args:
            case_comparisons (list of LazyLuna.Containers.Case_Comparison): list of case comparisons for calculation
        """
        self.view = view
        figtype = 'paired boxplot'
        rows, columns   = 1, 1
        self.set_size_inches(w=columns*11.0, h=(rows*6.0))
        ax = self.subplots(rows, columns)
        custom_palette  = sns.color_palette("Blues")
        custom_palette2 = sns.color_palette("Purples")
        swarm_palette   = sns.color_palette(["#061C36", "#061C36"])
        
        titlesize = 16
        labelsize = 14
        ticksize  = 12
        
        # Paired Boxplot for slice ms
        taskname1 = evals1[0].taskname
        taskname2 = evals2[0].taskname
        rows = []
        for eva1,eva2 in zip(evals1,evals2):
            for d in range(eva1.nr_slices):
                try:    val1 = np.nanmean(eva1.get_anno(d,0).get_pixel_values('lv_myo', eva1.get_img(d,0)).tolist())
                except: val1 = np.nan
                try:    val2 = np.nanmean(eva2.get_anno(d,0).get_pixel_values('lv_myo', eva2.get_img(d,0)).tolist())
                except: val2 = np.nan
                if np.isnan(val1) or np.isnan(val2): continue
                else: rows.extend([[eva1.name, eva1.studyuid, d, taskname1, val1], 
                                   [eva2.name, eva2.studyuid, d, taskname2, val2]])
        name = view.name + ' Slice Average'
        unit = '[ms]'
        df = DataFrame(rows, columns=['Casename', 'Studyuid', 'Slice', 'Taskname', name])
        sns.boxplot  (ax=ax, data=df, y='Taskname', x=name, width=0.4, palette=custom_palette, orient='h', linewidth=1)
        sns.swarmplot(ax=ax, data=df, y='Taskname', x=name, palette=swarm_palette, orient='h')
        ax.set_title(self.view.name +' Paired Boxplot (by slice)', fontsize=titlesize)
        ax.set_ylabel('')
        ax.set_xlabel(self.view.name + ' ' + unit, fontsize=labelsize)
        # Now connect the dots
        children = [c for c in ax.get_children() if isinstance(c, PathCollection)]
        locs1 = children[0].get_offsets()
        locs2 = children[1].get_offsets()
        set1 = df[df['Taskname']==taskname1][name]
        set2 = df[df['Taskname']==taskname2][name]
        sort_idxs1 = np.argsort(set1)
        sort_idxs2 = np.argsort(set2)
        # revert "ascending sort" through sort_idxs2.argsort(),
        # and then sort into order corresponding with set1
        locs2_sorted = locs2[sort_idxs2.argsort()][sort_idxs1]
        for i in range(locs1.shape[0]):
            x = [locs1[i, 0], locs2_sorted[i, 0]]
            y = [locs1[i, 1], locs2_sorted[i, 1]]
            ax.plot(x, y, color="black", alpha=0.4, linewidth=0.3)
        
        
        df_sorted_r1 = df[df['Taskname']==taskname1].sort_values(name)
        df_sorted_r2 = df[df['Taskname']==taskname2].sort_values(name)
        suids1 = df_sorted_r1['Studyuid'].tolist()
        suids2 = df_sorted_r2['Studyuid'].tolist()
        texts1 = [t+', slice: '+str(d) for t,d in zip(df_sorted_r1['Casename'].tolist(), df_sorted_r1['Slice'].tolist())]
        texts2 = [t+', slice: '+str(d) for t,d in zip(df_sorted_r2['Casename'].tolist(), df_sorted_r2['Slice'].tolist())]
        suids = [suids1, suids2]
        texts = [texts1, texts2]
        
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points", 
                            bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
        if not hasattr(self, 'canvas'): return
        
        def update_annot(collection, i, ind):
            pos = collection.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            annot.set_text(texts[i][ind['ind'][0]])
        
        def hover(event):
            vis = annot.get_visible()
            if event.inaxes==ax:
                for i, collection in enumerate(ax.collections):
                    cont, ind = collection.contains(event)
                    if cont:
                        update_annot(collection, i, ind)
                        annot.set_visible(True)
                        self.canvas.draw_idle()
                    else:
                        if vis:
                            annot.set_visible(False)
                            self.canvas.draw_idle()
        
        def onclick(event):
            vis = annot.get_visible()
            if event.inaxes==ax:
                try:
                    for i, collection in enumerate(ax.collections):
                        cont, ind = collection.contains(event)
                        if cont:
                            suid = suids[i][ind['ind'][0]]
                            eva1 = [eva for eva in evals1 if eva.studyuid==suid][0]
                            eva2 = [eva for eva in evals2 if eva.studyuid==suid][0]
                            for tab_name, tab in self.view.case_tabs.items(): 
                                t = tab()
                                t.make_tab(self.gui, view, eva1, eva2)
                                self.gui.tabs.addTab(t, tab_name+': '+eva1.name)
                except: print(traceback.format_exc()); pass
            if event.dblclick:
                try:
                    overviewtab = findCCsOverviewTab()
                    overviewtab.open_title_and_comments_popup(self, fig_name='T1_average_paired_boxplot')
                except: print(traceback.format_exc()); pass

        self.canvas.mpl_connect("motion_notify_event", hover)
        self.canvas.mpl_connect('button_press_event', onclick)
        self.subplots_adjust(top=0.90, bottom=0.15, left=0.15, right=0.93)
        self.canvas.draw()
        self.canvas.flush_events()
    
        
    
    def store(self, storepath, figurename='paired_boxplot_mapping_slice_average.png'):
        self.savefig(os.path.join(storepath, self.view.name+figurename), dpi=100, facecolor="#FFFFFF")
        return os.path.join(storepath, figurename)