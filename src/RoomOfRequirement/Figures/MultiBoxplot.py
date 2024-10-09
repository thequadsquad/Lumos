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

class MultiBoxplot(Visualization):
    def set_view(self, view):
        self.view   = view
        
    def set_canvas(self, canvas):
        self.canvas = canvas
        
    def set_gui(self, gui):
        self.gui = gui
        
    def visualize(self, cr_name, evals_list):
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
        
        
        #wofür baruchen wir das??? schließt das nur aus dass zweimal dasselbe kommt?
        
        self.task_list = []
        for i in range(0, len(evals_list)):
            self.task_list.append( evals_list[i][0].taskname)

        #farbschema anpassen?
        #colors_dict    = {0: 'yellow', 1: 'red', 2: 'blue', 3: 'green', 4: 'magenta', 5: 'indigo', 6: 'dark orange', 7: 'cyan', 8: 'dark red', 9: 'purple', 10: 'deep sky blue', 11: 'olive', 12: 'yellow green', 13: 'brownish orange', 14: 'tan', 15: 'violet red', 16: 'ecru', 17: 'aquamarine', 18: 'dusty rose', 19: 'spring green'}
        
        #custom_palette  = sns.xkcd_palette(colors_dict.values() )
        #swarm_palette   = sns.color_palette(["#061C36", "#061C36", "#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36"])
        #sns.xkcd_palette(list_colors)

        #custom_palette  = sns.mpl_palette("plasma", len(evals_list))
        #swarm_palette   = sns.color_palette(["#061C36", "#061C36", "#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36","#061C36"])
        
        
        
        custom_palette  = sns.color_palette([sns.color_palette("Blues")[1], sns.color_palette("Purples")[1]])
        swarm_palette   = sns.color_palette(["#061C36", "#061C36"])
        rows = []
        self.failed_cr_rows = []

        cr_dict = dict()
        for i in range(0, len(evals_list)):
            for eval in evals_list[i]:
                cr_dict[i] = cr.get_val(eval)
                #cr2 = cr.get_val(eval2)
                casename, studyuid = eval.name, eval.studyuid
                if np.isnan(cr_dict[i]) : self.failed_cr_rows.append([casename, studyuid])        #reicht das? 
                else: rows.extend([[casename, studyuid, self.task_list[i], cr_dict[i]]         ]) #in Lücke for i in ...?
        df = DataFrame(rows, columns=['casename', 'studyuid', 'taskname', cr_name])
        
        # Plot
        sns.boxplot  (ax=ax, data=df, y='taskname', x=cr_name, width=0.4, palette=custom_palette, orient='h', linewidth=1)
        sns.swarmplot(ax=ax, data=df, y='taskname', x=cr_name, palette=swarm_palette, orient='h')
        ax.set_title(cr_name+' Multi Boxplot', fontsize=14)
        ax.set_ylabel('')
        ax.set_xlabel(cr.name+' '+cr.unit, fontsize=12)
        # Now connect the dots
        locs = dict()
        children = [c for c in ax.get_children() if isinstance(c, PathCollection)]
        for i in range(0, len(evals_list)):
            locs[i] = children[i].get_offsets()
        
        for i in range(0, len(evals_list)-1):
            for j in range(0, locs[i].shape[0]):
                
                x, y = [locs[i][j,0], locs[i+1][j,0]], [locs[i][j,1], locs[i+1][j,1]]
                ax.plot(x, y, color="black", alpha=0.4, linewidth=0.3)
        suids = df['studyuid'].tolist()[::1]
        #suids = df['studyuid'].tolist()[::2]
        #print(df['studyuid'].tolist()[::2])
        #print(df['studyuid'].tolist()[::1])
        # sorts cr names by cr value

        #for i in range(0, len(evals_list)):
        #    for j in range(0, locs[i].shape[0]):
        #        dot[j] = { i : locs[i][j,0], locs[i][j,1] }

        print('len(evals_list)', len(evals_list))
        print('suids', suids)
        evals = { i : [eva for eva in evals_list[i]  if eva.studyuid in suids] for i in range(0, len(evals_list)) }
        print('evals: ', evals)
        texts = { i : df['casename'].tolist()[0::len(evals_list)]    for i in range(0, len(evals_list)) }
        print('texts: ', texts)


        
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points", 
                            bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
        if not hasattr(self, 'canvas'): return
        
        def update_annot(collection, i, ind):
            print('evals[i] ', evals[i])
            #print('evals[i].keys() ', evals[i].keys())
            print('evals[i][ind[ind][0]] ', evals[i][ind['ind'][0]])
            print('evals[i][ind[ind][0]].name ', evals[i][ind['ind'][0]].name)
            pos = collection.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            annot.set_text(evals[i][ind['ind'][0]].name)
            
            
        
        def hover(event):
            vis      = annot.get_visible()
            
            if event.inaxes==ax:
                for i, collection in enumerate(ax.collections):
                    cont, ind = collection.contains(event)
                    
                    if cont:
                        print('hover', cont, ind)
                        update_annot(collection, i, ind)
                        annot.set_visible(True)
                        self.canvas.draw_idle()
                        
                    else:
                        
                        if vis:
                            annot.set_visible(False)
                            self.canvas.draw_idle()
        
        def onclick(event):
            #eval_dict = dict()
            vis = annot.get_visible()
            if event.inaxes==ax:
                try:
                    for i, collection in enumerate(ax.collections):
                        print(i, collection)
                        cont, ind = collection.contains(event)
                        print(cont, ind)
                        if cont:
                            eval_ex = evals[i][ind['ind'][0]]
                            eval_dict = {j : [e for e in evals[j] if e.studyuid==eval_ex.studyuid][0] for j in range(0, len(evals_list)) }
                            print(eval_dict)
                            #eval2 = [e for e in evals2 if e.studyuid==eval_ex.studyuid][0]
                            for tab_name, tab in self.view.multi_case_tabs.items(): 
                                t = tab()
                                t.make_tab(self.gui, self.view, eval_dict)
                                self.gui.tabs.addTab(t, tab_name+': '+eval_dict[0].name)
                except: print(traceback.format_exc()); pass
            if event.dblclick:
                try:
                    overviewtab = findCCsOverviewTab()
                    overviewtab.open_title_and_comments_popup(self, fig_name=self.cr_name+'_multi_boxplot')
                except: print(traceback.format_exc()); pass
                            
        self.canvas.mpl_connect("motion_notify_event", hover)
        self.canvas.mpl_connect('button_press_event', onclick)
        #self.tight_layout()
        self.canvas.draw()
    
    def store(self, storepath, figurename='_multi_boxplot.png'):
        self.tight_layout()
        self.savefig(os.path.join(storepath, self.cr_name+figurename), dpi=300, facecolor="#FFFFFF")
        return os.path.join(storepath, self.cr_name+figurename)
        