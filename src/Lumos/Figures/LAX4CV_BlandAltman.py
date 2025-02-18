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
        

class LAX4CV_BlandAltman(Visualization):
    def visualize(self, view, evals1, evals2, with_swarmplot=True):
        """Takes a list of case_comparisons and presents a visualization of several blandaltman plots for areas
        
        Args:
            view (LazyLuna.Views.View): A LAX_CINE View
            ccs (list of LazyLuna.Containers.Case_Comparison): The blandaltmans are calculated for this list of case_comparisons
        """
        rows, columns   = 4, 2
        self.set_size_inches(w=columns*11.0, h=(rows*7.0))
        axes = self.subplots(rows, columns)
        custom_palette  = sns.color_palette("Blues")
        custom_palette2 = sns.color_palette("Purples")
        swarm_palette   = sns.color_palette(["#061C36", "#061C36"])
        
        
        cps = [view.clinical_parameters[cpn] for cpn in ['4CV_LAESAREA', '4CV_LAEDAREA', '4CV_RAESAREA', '4CV_RAEDAREA']]
        cpname2diff = dict()
        
        # Clinical Parameter Bland Altman Plots
        for i, cp in enumerate(cps):
            cpn  = cp.name
            ax   = axes[i//2][i%2]
            cpname2diff[cpn]=[]
            # for scatter plot
            avgs, diffs = [], []
            for e1,e2 in zip(evals1,evals2):
                val1, val2, diff = cp.get_val(e1), cp.get_val(e2), cp.get_val_diff(e1,e2)
                if np.isnan(val1) or np.isnan(val2) or np.isnan(diff): continue
                cpname2diff[cpn].append(diff) # use for tol range below
                avgs.append((val1+val2)/2.0); diffs.append(diff)
            if len(avgs)>0:
                sns.scatterplot(ax=ax, x=avgs, y=diffs, markers='o', 
                                palette=swarm_palette, size=np.abs(diffs), s=10, legend=False)
                ax.set_title(cpn + ' Bland Altman', fontsize=26)
                ax.axhline(np.mean(diffs), ls='-', c='.2')
                ax.axhline(np.mean(diffs)+1.96*np.std(diffs), ls=":", c=".2")
                ax.axhline(np.mean(diffs)-1.96*np.std(diffs), ls=":", c=".2")
            else:
                ax.set_title('No ' + cpn + ' Values Available', fontsize=26)
            ax.set_xlabel('[#]' if 'P_' in cpn else '[cm²]', fontsize=20)
            ax.set_ylabel('[#]' if 'P_' in cpn else '[cm²]', fontsize=20)
            ax.tick_params(axis='both', which='major', labelsize=20)
        yabs_max = max([max(axes[i//2,i%2].get_ylim(),key=abs) for i in range(len(cps))])+2
        for i in range(len(cps)): axes[i//2,i%2].set_ylim(ymin=-yabs_max, ymax=yabs_max)
            
        # Tolerance Range
        for i, crn in enumerate(['4CV_LAEDAREA', '4CV_RAEDAREA']):
            ax = axes[2,i]
            ax.set_title(crn + ' Equivalence Test', fontsize=26)
            cr = view.clinical_parameters[crn]
            ax.axhspan(-cr.tol_range, cr.tol_range, facecolor='0.6', alpha=0.5)
            alpha = 0.5 if with_swarmplot else 0.0
            sns.swarmplot(ax=ax, y=cpname2diff[crn], palette=sns.color_palette("Blues")[4:],
                          dodge=True, size=5, alpha=alpha)
            ci = 1.96 * np.std(cpname2diff[crn]) / np.sqrt(len(cpname2diff[crn]))
            #ax.errorbar([crn], [np.mean(cpname2diff[crn])], yerr=ci, fmt ='o', c='r')
            sns.pointplot(ax=ax, y=cpname2diff[crn], errorbar=("ci", 95), color='r')
            maxx = np.max([np.abs(np.min(cpname2diff[crn])), np.abs(np.max(cpname2diff[crn])), 
                           np.abs(np.mean(cpname2diff[crn])-ci), np.abs(np.mean(cpname2diff[crn])+ci), 
                           cr.tol_range])
            ax.set_ylim(ymin=-maxx-2, ymax=maxx+2)
            ax.tick_params(axis='both', which='major', labelsize=20)
            ax.set_ylabel(cr.name + ' ' + cr.unit, fontsize=20)
            ax.set_xlabel(cr.name, fontsize=20)
            
                
        # Dice metric for LA area?
        for i, cname in enumerate(['la', 'ra']):
            ax = axes[3,i]
            dice_rows = []
            dice_metric = DiceMetric()
            for eva1, eva2 in zip(evals1, evals2):
                phase_names = view.clinical_phases[cname]
                esp, edp = [view.clinical_parameters[p] for p in phase_names]
                for p_i, (p1,p2) in enumerate([(esp.get_val(eva1),esp.get_val(eva2)), (edp.get_val(eva1),edp.get_val(eva2))]):
                    for d in range(eva1.nr_slices):
                        try:
                            anno1, anno2 = eva1.get_anno(d,p1), eva2.get_anno(d,p2)
                            if not anno1.has_contour(cname) or not anno2.has_contour(cname): continue
                            dice_val = dice_metric.get_val(anno1.get_contour(cname), anno2.get_contour(cname))
                            dice_rows.append(['ES & ED', dice_val])
                            dice_rows.append(['ES' if p_i==0 else 'ED', dice_val])
                        except: continue
            df = pandas.DataFrame(dice_rows, columns=['Phase', 'Dice'])
            dicebp = sns.boxplot(ax=ax, x="Phase", y="Dice", data=df, width=0.5)
            sns.swarmplot(       ax=ax, x="Phase", y="Dice", data=df, palette=swarm_palette)#, dodge=True)
            handles, labels = ax.get_legend_handles_labels()
            ax.set_title(cname.upper()+'Dice Values by Phase', fontsize=26)
            ax.set_ylabel('[%]', fontsize=20)
            ax.set_xlabel("", fontsize=20)
            ax.set_ylim(ymin=75, ymax=101)
            for i, boxplot in enumerate(dicebp.patches):
                if i%2==0: boxplot.set_facecolor(custom_palette [i//2+1])
                else:      boxplot.set_facecolor(custom_palette2[i//2+1])
            ax.tick_params(axis='both', which='major', labelsize=20)
            
        sns.despine()
        self.subplots_adjust(left=0.075, bottom=0.05, right=0.95, top=0.95, wspace=0.15, hspace=0.25)
        
    
    
    def store(self, storepath, figurename='lax_areas_bland_altman.png'):
        self.tight_layout()
        self.savefig(os.path.join(storepath, figurename), dpi=100, facecolor="#FFFFFF")
        return os.path.join(storepath, figurename)