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


class SAX_BlandAltman(Visualization):
    def visualize(self, view, evals1, evals2):
        """Takes a list of case_comparisons and presents Blandaltmans for several Clinical Results in one figure
        
        Args:
            case_comparisons (list of LazyLuna.Containers.Case_Comparison): list of case comparisons for calculation
        """
        rows, columns   = 4, 2
        self.set_size_inches(w=columns*11.0, h=(rows*6.0))
        axes = self.subplots(rows, columns)
        custom_palette  = sns.color_palette("Blues")
        custom_palette2 = sns.color_palette("Purples")
        swarm_palette   = sns.color_palette(["#061C36", "#061C36"])
        cps = [view.clinical_parameters[cpn] for cpn in ['LVESV', 'LVEDV', 'LVEF', 'LVM', 'RVESV', 'RVEDV', 'RVEF']]
        
        # Clinical Parameter Bland Altman Plots
        for i, cp in enumerate(cps):
            print(i, ' of ', len(cps))
            cpn  = cp.name
            ax   = axes[i//2][i%2]
            # for scatter plot
            avgs, diffs = [], []
            for e1,e2 in zip(evals1,evals2):
                val1, val2, diff = cp.get_val(e1), cp.get_val(e2), cp.get_val_diff(e1,e2)
                if np.isnan(val1) or np.isnan(val2) or np.isnan(diff): continue
                avgs.append((val1+val2)/2.0); diffs.append(diff)
            if len(avgs)>0:
                sns.scatterplot(ax=ax, x=avgs, y=diffs, markers='o', size=np.abs(diffs), legend=False)
                ax.set_title(cpn + ' Bland Altman', fontsize=26)
                ax.axhline(y=np.mean(diffs), ls='-', c='.2')
                ax.axhline(np.mean(diffs)+1.96*np.std(diffs), ls=":", c=".2")
                ax.axhline(np.mean(diffs)-1.96*np.std(diffs), ls=":", c=".2")
            else:
                ax.set_title('No ' + cpn + ' Values Available', fontsize=26)
            ax.set_xlabel('[%]' if 'EF' in cpn else '[ml]' if 'ESV' in cpn or 'EDV' in cpn else '[g]', fontsize=20)
            ax.set_ylabel('[%]' if 'EF' in cpn else '[ml]' if 'ESV' in cpn or 'EDV' in cpn else '[g]', fontsize=20)
            ax.tick_params(axis='both', which='major', labelsize=20)
            yabs_max = abs(max(ax.get_ylim(), key=abs))
            ax.set_ylim(ymin=-yabs_max, ymax=yabs_max)
            if 'EF' in cpn:                  ax.set_ylim(ymin=-20, ymax=20)
            if 'ESV' in cpn or 'EDV' in cpn: ax.set_ylim(ymin=-45, ymax=45)
            if 'MYOMASS' in cpn:             ax.set_ylim(ymin=-30, ymax=30)
            
        # Annotation Differences
        dice_metric = DiceMetric()
        dice_rows = []
        for eva1, eva2 in zip(evals1, evals2):
            esp, edp = view.clinical_phases['lv_endo']
            esp, edp = view.clinical_parameters[esp], view.clinical_parameters[edp]
            p1,  p2  = esp.get_val(eva1), esp.get_val(eva2)
            try:
                lv_dices_all  = [dice_metric.get_val(eva1.get_anno(d,p1).get_contour('lv_endo'),
                                                     eva2.get_anno(d,p2).get_contour('lv_endo'))
                                 for d in range(eva1.nr_slices)]
                lv_dices_both = [dice_metric.get_val(eva1.get_anno(d,p1).get_contour('lv_endo'), 
                                                     eva2.get_anno(d,p2).get_contour('lv_endo')) 
                                 for d in range(eva1.nr_slices) 
                                 if eva1.get_anno(d,p1).has_contour('lv_endo') and eva2.get_anno(d,p2).has_contour('lv_endo')]
                p1,  p2  = edp.get_val(eva1), edp.get_val(eva2)
                lv_dices_all  += [dice_metric.get_val(eva1.get_anno(d,p1).get_contour('lv_endo'), 
                                                      eva2.get_anno(d,p2).get_contour('lv_endo'))
                                  for d in range(eva1.nr_slices)]
                lv_dices_both += [dice_metric.get_val(eva1.get_anno(d,p1).get_contour('lv_endo'), 
                                                      eva2.get_anno(d,p2).get_contour('lv_endo')) 
                                  for d in range(eva1.nr_slices) 
                                  if eva1.get_anno(d,p1).has_contour('lv_endo') and eva2.get_anno(d,p2).has_contour('lv_endo')]
            except:
                lv_dices_all, lv_dices_both = [],[]
            
            esp, edp = view.clinical_phases['rv_endo']
            esp, edp = view.clinical_parameters[esp], view.clinical_parameters[edp]
            try:
                p1,  p2  = esp.get_val(eva1), esp.get_val(eva2)
                rv_dices_all  = [dice_metric.get_val(eva1.get_anno(d,p1).get_contour('rv_endo'), 
                                                     eva2.get_anno(d,p2).get_contour('rv_endo'))
                                 for d in range(eva1.nr_slices)]
                rv_dices_both = [dice_metric.get_val(eva1.get_anno(d,p1).get_contour('rv_endo'), 
                                                     eva2.get_anno(d,p2).get_contour('rv_endo')) 
                                 for d in range(eva1.nr_slices) 
                                 if eva1.get_anno(d,p1).has_contour('rv_endo') and eva2.get_anno(d,p2).has_contour('rv_endo')]
                p1,  p2  = edp.get_val(eva1), edp.get_val(eva2)
                rv_dices_all  += [dice_metric.get_val(eva1.get_anno(d,p1).get_contour('rv_endo'), 
                                                      eva2.get_anno(d,p2).get_contour('rv_endo'))
                                  for d in range(eva1.nr_slices)]
                rv_dices_both += [dice_metric.get_val(eva1.get_anno(d,p1).get_contour('rv_endo'), 
                                                      eva2.get_anno(d,p2).get_contour('rv_endo')) 
                                  for d in range(eva1.nr_slices) 
                                  if eva1.get_anno(d,p1).has_contour('rv_endo') and eva2.get_anno(d,p2).has_contour('rv_endo')]
            except:
                rv_dices_all, rv_dices_both = [],[]
            
            edp = view.clinical_phases['lv_myo']
            edp = view.clinical_parameters[edp[0]]
            try:
                p1,  p2  = edp.get_val(eva1), edp.get_val(eva2)
                myo_dices_all  += [dice_metric.get_val(eva1.get_anno(d,p1).get_contour('lv_myo'), 
                                                       eva2.get_anno(d,p2).get_contour('lv_myo'))
                                   for d in range(eva1.nr_slices)]
                myo_dices_both += [dice_metric.get_val(eva1.get_anno(d,p1).get_contour('lv_myo'), 
                                                       eva2.get_anno(d,p2).get_contour('lv_myo')) 
                                   for d in range(eva1.nr_slices) 
                                   if eva1.get_anno(d,p1).has_contour('lv_myo') and eva2.get_anno(d,p2).has_contour('lv_myo')]
            except:
                myo_dices_all, myo_dices_both = [],[]
            
            all_dices_all  = [np.nanmean(lv_dices_all),  np.nanmean(rv_dices_all),  np.nanmean(myo_dices_all) ]
            all_dices_both = [np.nanmean(lv_dices_both), np.nanmean(rv_dices_both), np.nanmean(myo_dices_both)]
            
            # how many rows - how divided????
            dice_rows.extend([[eva1.name, 'All',     'all',  np.nanmean(all_dices_all) ],
                              [eva1.name, 'All',     'both', np.nanmean(all_dices_both)],
                              [eva1.name, 'LV Endo', 'all',  np.nanmean(lv_dices_all)  ],
                              [eva1.name, 'LV Endo', 'both', np.nanmean(lv_dices_both) ],
                              [eva1.name, 'LV Myo',  'all',  np.nanmean(myo_dices_all) ],
                              [eva1.name, 'LV Myo',  'both', np.nanmean(myo_dices_both)],
                              [eva1.name, 'RV Endo', 'all',  np.nanmean(rv_dices_all)  ],
                              [eva1.name, 'RV Endo', 'both', np.nanmean(rv_dices_both) ]])
        
        ax = axes[3][1]
        df = pandas.DataFrame(dice_rows, columns=['Name', 'Contour Type', 'All or Both', 'Case Average'])
        dicebp = sns.boxplot(ax=ax, x="Contour Type", y="Case Average", hue='All or Both', data=df, width=0.8)
        sns.swarmplot(ax=ax, x="Contour Type", y="Case Average", hue='All or Both', data=df, palette=swarm_palette, dodge=True)
        handles, labels = ax.get_legend_handles_labels()
        handles[0].set(color=custom_palette[3])
        handles[1].set(color=custom_palette2[3])
        ax.set_title('Dice Values by Contour Type', fontsize=26)
        ax.legend(handles[:2], labels[:2], title="Annotated by both", fontsize=18)
        ax.set_ylabel('[%]', fontsize=20)
        ax.set_xlabel("", fontsize=20)
        ax.set_ylim(ymin=65, ymax=101)
        for i, boxplot in enumerate(dicebp.patches):
            if i%2==0: boxplot.set_facecolor(custom_palette [i//2+1])
            else:      boxplot.set_facecolor(custom_palette2[i//2+1])
        ax.tick_params(axis='both', which='major', labelsize=20)
        sns.despine()
        self.subplots_adjust(left=0.075, bottom=0.05, right=0.95, top=0.95, wspace=0.15, hspace=0.25)
        
    
    def store(self, storepath, figurename='clinical_results_bland_altman.png'):
        print('Storage path: ', os.path.join(storepath, figurename))
        self.savefig(os.path.join(storepath, figurename), dpi=100, facecolor="#FFFFFF")
        return os.path.join(storepath, figurename)