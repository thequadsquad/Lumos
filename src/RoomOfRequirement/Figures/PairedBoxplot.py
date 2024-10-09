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
from RoomOfRequirement import ClinicalResults
from RoomOfRequirement import utils
from RoomOfRequirement.Figures.Visualization import *

from RoomOfRequirement.utils import findMainWindow, findCCsOverviewTab

class PairedBoxplot(Visualization):
    def set_view(self, view):
        self.view   = view
        
    def set_canvas(self, canvas):
        self.canvas = canvas
        
    def set_gui(self, gui):
        self.gui = gui
        
    def visualize(self, cr_name, evals1, evals2):
        """Takes a list of case_comparisons and presents a Paired Boxplot for a Clinical Result
        
        Note:
            requires setting values first:
            - self.set_view(View)
            - self.set_canvas(canvas)
            - self.set_gui(gui)
        
        Args:
            case_comparisons (list of LazyLuna.Containers.Case_Comparison): list of case comparisons for calculation
            cr_name (str): name of Clinical Result
        """
        self.cr_name = cr_name
        #get class name from cr name
        cr = self.view.clinical_parameters[cr_name]
        
        self.clf()
        ax = self.add_subplot(111, position=[0.16, 0.16, 0.68, 0.68])
        #self.set_size_inches(w=7.5, h=10)
        taskname1 = evals1[0].taskname
        taskname2 = evals2[0].taskname
        if taskname1==taskname2: taskname2=' '+taskname2
        custom_palette  = sns.color_palette([sns.color_palette("Blues")[1], sns.color_palette("Purples")[1]])
        swarm_palette   = sns.color_palette(["#061C36", "#061C36"])
        rows = []
        self.failed_cr_rows = []
        for eval1, eval2 in zip(evals1, evals2):
            cr1 = cr.get_val(eval1)
            cr2 = cr.get_val(eval2)
            casename, studyuid = eval1.name, eval1.studyuid
            if np.isnan(cr1) or np.isnan(cr2): self.failed_cr_rows.append([casename, studyuid])
            else: rows.extend([[casename, studyuid, taskname1, cr1], [casename, studyuid, taskname2, cr2]])
        df = DataFrame(rows, columns=['casename', 'studyuid', 'taskname', cr_name])
        
        # Plot
        sns.boxplot  (ax=ax, data=df, y='taskname', x=cr_name, width=0.4, palette=custom_palette, orient='h', linewidth=1)
        sns.swarmplot(ax=ax, data=df, y='taskname', x=cr_name, palette=swarm_palette, orient='h')
        ax.set_title(cr_name+' Paired Boxplot', fontsize=14)
        ax.set_ylabel('')
        ax.set_xlabel(cr.name+' '+cr.unit, fontsize=12)
        # Now connect the dots
        children = [c for c in ax.get_children() if isinstance(c, PathCollection)]
        locs1 = children[0].get_offsets()
        locs2 = children[1].get_offsets()
        
        for i in range(locs1.shape[0]):
            x, y = [locs1[i,0], locs2[i,0]], [locs1[i,1], locs2[i,1]]
            ax.plot(x, y, color="black", alpha=0.4, linewidth=0.3)
        
        suids = df['studyuid'].tolist()[::2]
        # sorts cr names by cr value
        evas1,  evas2  = [eva for eva in evals1 if eva.studyuid in suids], [eva for eva in evals2 if eva.studyuid in suids]
        texts1, texts2 = df['casename'].tolist()[0::2], df['casename'].tolist()[1::2]
        evals  = [evas1,  evas2]
        texts  = [texts1, texts2]
        
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
                            eval_ex = evals[i][ind['ind'][0]]
                            eval1 = [e for e in evals1 if e.studyuid==eval_ex.studyuid][0]
                            eval2 = [e for e in evals2 if e.studyuid==eval_ex.studyuid][0]
                            for tab_name, tab in self.view.case_tabs.items(): 
                                t = tab()
                                t.make_tab(self.gui, self.view, eval1, eval2)
                                self.gui.tabs.addTab(t, tab_name+': '+eval1.name)
                except: print(traceback.format_exc()); pass
            if event.dblclick:
                try:
                    overviewtab = findCCsOverviewTab()
                    overviewtab.open_title_and_comments_popup(self, fig_name=self.cr_name+'_paired_boxplot')
                except: print(traceback.format_exc()); pass
                            
        self.canvas.mpl_connect("motion_notify_event", hover)
        self.canvas.mpl_connect('button_press_event', onclick)
        self.tight_layout()
        self.canvas.draw()
    
    def store(self, storepath, figurename='_paired_boxplot.png'):
        self.tight_layout()
        self.savefig(os.path.join(storepath, self.cr_name+figurename), dpi=300, facecolor="#FFFFFF")
        return os.path.join(storepath, self.cr_name+figurename)
