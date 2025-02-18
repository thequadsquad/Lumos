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

from Lumos.utils import findMainWindow, findCCsOverviewTab

        
class BlandAltman(Visualization):
    def set_view(self, view):     self.view   = view
    def set_canvas(self, canvas): self.canvas = canvas
    def set_gui(self, gui):       self.gui    = gui
        
    def visualize(self, cr_name, evals1, evals2):
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
        
        self.cr_name = cr_name
        #get class name from cr name
        cr = self.view.clinical_parameters[cr_name]
        
        self.clf()
        ax = self.add_subplot(111, position=[0.16, 0.16, 0.68, 0.68])
        swarm_palette   = sns.color_palette(["#061C36", "#061C36"])
        
        rows = []
        self.failed_cr_rows = []
        for eval1, eval2 in zip(evals1, evals2):
            cr1, cr2, cr_diff = cr.get_val(eval1), cr.get_val(eval2), cr.get_val_diff(eval1, eval2)
            if np.isnan(cr1) or np.isnan(cr2): self.failed_cr_rows.append([eval1.name, eval1.studyuid])
            else: rows.append([eval1.name, eval1.studyuid, (cr1+cr2)/2.0, cr_diff])
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
        
        def hover(event):
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
        
        def onclick(event):
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
        self.tight_layout()
        self.canvas.draw()
    
    def store(self, storepath, figurename='_bland_altman.png'):
        self.tight_layout()
        self.savefig(os.path.join(storepath, self.cr_name+figurename), dpi=300, facecolor="#FFFFFF")
        return os.path.join(storepath, self.cr_name+figurename)
    