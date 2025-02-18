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


class Mapping_DiceBySlice(Visualization):
        
    def set_canvas(self, canvas):
        self.canvas = canvas
        
    def set_gui(self, gui):
        self.gui = gui
    
    def visualize(self, view, evals1, evals2):
        """Takes a list of case_comparisons and presents Blandaltmans for several Clinical Results in one figure
        
        Args:
            case_comparisons (list of LazyLuna.Containers.Case_Comparison): list of case comparisons for calculation
        """
        self.view = view
        rows, columns   = 1, 1
        self.set_size_inches(w=columns*11.0, h=(rows*6.0))
        ax = self.subplots(rows, columns)
        custom_palette  = sns.color_palette("Blues")
        custom_palette2 = sns.color_palette("Purples")
        swarm_palette   = sns.color_palette(["#061C36", "#061C36"])
        
        titlesize = 16
        labelsize = 14
        ticksize  = 12
        
        rows = []
        for eva1,eva2 in zip(evals1,evals2):
            for d in range(eva1.nr_slices):
                for conttype in ['lv_endo', 'lv_myo']:
                    try:
                        if not eva1.get_anno(d,0).has_contour(conttype) or not eva2.get_anno(d,0).has_contour(conttype): continue
                        cont1 = eva1.get_anno(d,0).get_contour(conttype)
                        cont2 = eva2.get_anno(d,0).get_contour(conttype)
                        dice, hd = utils.dice(cont1, cont2), utils.hausdorff(cont1, cont2)
                        rows.append([eva1.name, eva1.studyuid, d, conttype, dice, hd])
                    except Exception as e: print(eva1.name, d, e)
        df = DataFrame(rows, columns=['Casename', 'Studyuid', 'Slice', 'Contour Type', 'Dice', 'HD'])
        ax.set_title('Dice (by slice)', fontsize=titlesize)
        sns.boxplot  (ax=ax, x="Dice", y="Contour Type", data=df, palette=custom_palette, width=0.4, orient='h')
        sns.swarmplot(ax=ax, x="Dice", y="Contour Type", data=df, palette=swarm_palette, dodge=True, orient='h')
        ax.set_xlabel('Dice [%]', fontsize=labelsize)
        ax.set_ylabel("", fontsize=labelsize)
        xmin = np.max([np.min(df['Dice']) - 5, 0])
        ax.set_xlim(xmin=xmin, xmax=111)
        ax.tick_params(axis='both', which='major', labelsize=ticksize)
        sns.despine()
        
        studyuids  = list(set(df['Studyuid'].tolist()))
        suids_myo  = df[df['Contour Type']=='lv_myo' ].sort_values('Dice')['Studyuid'].tolist()
        suids_endo = df[df['Contour Type']=='lv_endo'].sort_values('Dice')['Studyuid'].tolist()
        texts_myo  = [t+', slice: '+str(d) for t,d in zip(df[df['Contour Type']=='lv_myo' ].sort_values('Dice')['Casename'].tolist(), df[df['Contour Type']=='lv_myo' ].sort_values('Dice')['Slice'].tolist())]
        texts_endo = [t+', slice: '+str(d) for t,d in zip(df[df['Contour Type']=='lv_endo'].sort_values('Dice')['Casename'].tolist(), df[df['Contour Type']=='lv_endo'].sort_values('Dice')['Slice'].tolist())]
        texts = [texts_endo, texts_myo]
        suids = [suids_endo, suids_myo]
        
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
                    overviewtab.open_title_and_comments_popup(self, fig_name='Dice_per_slice_paired_boxplot')
                except: print(traceback.format_exc()); pass

        self.canvas.mpl_connect("motion_notify_event", hover)
        self.canvas.mpl_connect('button_press_event', onclick)
        ax.tick_params(axis='both', which='major', labelsize=ticksize)
        self.subplots_adjust(top=0.90, bottom=0.15, left=0.15, right=0.93)
        self.canvas.draw()
        self.canvas.flush_events()
    
        
    
    def store(self, storepath, figurename='mapping_slice_average_blandaltman.png'):
        self.savefig(os.path.join(storepath, self.view.name+figurename), dpi=100, facecolor="#FFFFFF")
        return os.path.join(storepath, self.view.name+figurename)