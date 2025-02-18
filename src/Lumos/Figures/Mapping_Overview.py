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


class Mapping_Overview(Visualization):
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
        
        titlesize=26
        labelsize=20
        ticksize=20
        
        cp = view.clinical_parameters[[k for k in view.clinical_parameters if 'GLOBAL' in k][0]]
        val1, val2, avgs, diffs = [], [], [], []
        for eva1,eva2 in zip(evals1,evals2):
            val1 .append(cp.get_val(eva1))
            val2 .append(cp.get_val(eva2))
            avgs .append((cp.get_val(eva1)+cp.get_val(eva2))/2.0)
            diffs.append(cp.get_val_diff(eva1,eva2))
        
        # Bland Altman
        ax = axes[0][0]
        ax.set_title('Mapping Overview', fontsize=titlesize)
        sns.scatterplot(ax=ax, x=avgs, y=diffs, markers='o', palette=swarm_palette, size=np.abs(diffs), s=10, legend=False)
        avg_diff, std_diff = np.nanmean(diffs), np.nanstd(diffs)
        ax.axhline(avg_diff, ls="-", c=".2")
        ax.axhline(avg_diff+1.96*std_diff, ls=":", c=".2"); ax.axhline(avg_diff-1.96*std_diff, ls=":", c=".2")
        ax.set_xlabel(cp.name+' '+cp.unit, fontsize=labelsize); ax.set_ylabel(cp.name+' '+cp.unit, fontsize=labelsize)
        yabs_max = abs(max(ax.get_ylim(), key=abs)) + 10
        ax.set_ylim(ymin=-yabs_max, ymax=yabs_max)
        
        # Paired Boxplot
        ax = axes[0][1]
        taskname1, taskname2 = evals1[0].taskname, evals2[0].taskname
        if taskname1==taskname2: taskname2+=' '
        rows = []
        for eva1,eva2 in zip(evals1,evals2):
            val1, val2 = cp.get_val(eva1), cp.get_val(eva2)
            if np.isnan(val1) or np.isnan(val2): continue
            rows.extend([[eva1.name, eva1.studyuid, taskname1, val1],[eva1.name, eva1.studyuid, taskname2, val2]])
        df = DataFrame(rows, columns=['Casename', 'Studyuid', 'Taskname', cp.name])
        # Plot
        sns.boxplot  (ax=ax, data=df, y='Taskname', x=cp.name, width=0.4, palette=custom_palette, orient='h', linewidth=1)
        sns.swarmplot(ax=ax, data=df, y='Taskname', x=cp.name, palette=swarm_palette, orient='h')
        ax.set_title(cp.name+' Paired Boxplot', fontsize=titlesize)
        ax.set_ylabel(''); ax.set_xlabel(cp.name+' '+cp.unit, fontsize=22)
        # Now connect the dots
        children = [c for c in ax.get_children() if isinstance(c, PathCollection)]
        locs1, locs2 = children[0].get_offsets(), children[1].get_offsets()
        set1, set2 = df[df['Taskname']==taskname1][cp.name], df[df['Taskname']==taskname2][cp.name]
        sort_idxs1, sort_idxs2 = np.argsort(set1), np.argsort(set2)
        # revert "ascending sort" through sort_idxs2.argsort(),
        # and then sort into order corresponding with set1
        locs2_sorted = locs2[sort_idxs2.argsort()][sort_idxs1]
        for i in range(locs1.shape[0]):
            x, y = [locs1[i, 0], locs2_sorted[i, 0]], [locs1[i, 1], locs2_sorted[i, 1]]
            ax.plot(x, y, color="black", alpha=0.4, linewidth=0.3)
        
        # Bland Altman for slice ms
        ax = axes[1][0]
        rows = []
        for i, (eva1,eval2) in enumerate(zip(evals1,evals2)):
            for d in range(eva1.nr_slices):
                try:
                    val1 = np.nanmean(eva1.get_anno(d,0).get_pixel_values('lv_myo', eva1.get_img(d,0)).tolist())
                    val2 = np.nanmean(eva2.get_anno(d,0).get_pixel_values('lv_myo', eva2.get_img(d,0)).tolist())
                    if np.isnan(val1) or np.isnan(val2): continue
                    rows.append([(val1+val2)/2.0, val1-val2])
                except Exception as e: print(eva1.name, d, e)
        df = DataFrame(rows, columns=['Average', 'Difference'])
        ax.set_title(view.name[4:] + ' Bland Altman (by slice & segmented by both)', fontsize=titlesize)
        sns.scatterplot(ax=ax, x='Average', y='Difference', data=df, markers='o', 
                        palette=swarm_palette, size=np.abs(df['Difference']), s=10, legend=False)
        avg_diff, std_diff = df['Difference'].mean(), df['Difference'].std()
        ax.axhline(avg_diff, ls="-", c=".2")
        ax.axhline(avg_diff+1.96*std_diff, ls=":", c=".2"); ax.axhline(avg_diff-1.96*std_diff, ls=":", c=".2")
        ax.set_xlabel(view.name[4:]+' '+cp.unit, fontsize=labelsize)
        ax.set_ylabel(view.name[4:]+' '+cp.unit, fontsize=labelsize)
        yabs_max = abs(max(ax.get_ylim(), key=abs)) + 10
        ax.set_ylim(ymin=-yabs_max, ymax=yabs_max)
        
        
        # Paired Boxplot for slice ms
        ax = axes[1][1]
        rows = []
        segm_by_both, segm_by_r1, segm_by_r2, segm_by_none = 0, 0, 0, 0
        for i, (eva1,eva2) in enumerate(zip(evals1,evals2)):
            for d in range(eva1.nr_slices):
                try:    val1 = np.nanmean(eva1.get_anno(d,0).get_pixel_values('lv_myo', eva1.get_img(d,0)).tolist())
                except: val1 = np.nan
                try:    val2 = np.nanmean(eva2.get_anno(d,0).get_pixel_values('lv_myo', eva2.get_img(d,0)).tolist())
                except: val2 = np.nan
                if not np.isnan(val1) and not np.isnan(val2): segm_by_both += 1
                if not np.isnan(val1) and     np.isnan(val2): segm_by_r1   += 1
                if     np.isnan(val1) and not np.isnan(val2): segm_by_r2   += 1
                if     np.isnan(val1) and     np.isnan(val2): segm_by_none += 1
                if np.isnan(val1) or np.isnan(val2): continue
                rows.extend([[eva1.name, d, taskname1, val1], [eva2.name, d, taskname2, val2]])
        df = DataFrame(rows, columns=['Casename', 'Slice', 'Taskname', cp.name])
        sns.boxplot  (ax=ax, data=df, y='Taskname', x=cp.name, width=0.4, palette=custom_palette, orient='h', linewidth=1)
        sns.swarmplot(ax=ax, data=df, y='Taskname', x=cp.name, palette=swarm_palette, orient='h')
        ax.set_title(view.name[4:]+' Paired Boxplot (by slice & segmented by both)', fontsize=titlesize)
        ax.set_ylabel(''); ax.set_xlabel(view.name[4:]+ ' ' + cp.unit, fontsize=labelsize)
        # Now connect the dots
        children = [c for c in ax.get_children() if isinstance(c, PathCollection)]
        locs1, locs2 = children[0].get_offsets(), children[1].get_offsets()
        set1, set2 = df[df['Taskname']==taskname1][cp.name], df[df['Taskname']==taskname2][cp.name]
        sort_idxs1, sort_idxs2 = np.argsort(set1), np.argsort(set2)
        # revert "ascending sort" through sort_idxs2.argsort(),
        # and then sort into order corresponding with set1
        locs2_sorted = locs2[sort_idxs2.argsort()][sort_idxs1]
        for i in range(locs1.shape[0]):
            x, y = [locs1[i,0], locs2_sorted[i,0]], [locs1[i,1], locs2_sorted[i,1]]
            ax.plot(x, y, color="black", alpha=0.4, linewidth=0.3)
        
        # histogram of counts
        ax = axes[2][0]
        ax.set_ylabel('Count [#]', fontsize=labelsize)
        ax.set_title('Barplot of Annotated / Overlooked Images', fontsize=titlesize)
        sns.barplot(x=['Segm. by \nboth', 'Segm. only \nby '+taskname1, 'Segm. only \nby '+taskname2, 'Segm. by \nnone'], 
                    y=[segm_by_both, segm_by_r1, segm_by_r2, segm_by_none], ax=ax, palette=custom_palette2[2:])
        
        # Tolerance ranges
        ax = axes[2][1]
        ax.axhspan(-cp.tol_range, cp.tol_range, facecolor='0.6', alpha=0.5)
        alpha = 0.5 
        sns.swarmplot(ax=ax, y=diffs, palette=sns.color_palette("Blues")[4:], dodge=True, size=5, alpha=alpha)
        ci = 1.96 * np.nanstd(diffs) / np.sqrt(len(diffs))
        sns.pointplot(ax=ax, y=diffs, errorbar=("ci", 95), color='r')
        maxx = np.max([np.abs(np.nanmin(diffs)), np.abs(np.nanmax(diffs)),
                       np.abs(np.nanmean(diffs)-ci), np.abs(np.nanmean(diffs)+ci), 
                       cp.tol_range])
        ax.set_title(view.name[4:]+' Tolerance Range (by slice & segmented by both)', fontsize=titlesize)
        ax.set_ylim(ymin=-maxx-10, ymax=maxx+10)
        ax.set_ylabel(cp.name + ' ' + cp.unit, fontsize=labelsize)
        ax.set_xlabel(cp.name, fontsize=labelsize)
        
        
        # Dice Values
        ax = axes[3][0]
        rows = []
        for i, (eva1,eva2) in enumerate(zip(evals1,evals2)):
            for d in range(eva1.nr_slices):
                anno1, anno2 = eva1.get_anno(d,0), eva2.get_anno(d,0)
                for conttype in ['lv_endo', 'lv_myo']:
                    try:
                        if not anno1.has_contour(conttype) or not anno2.has_contour(conttype): continue
                        cont1, cont2 = anno1.get_contour(conttype), anno2.get_contour(conttype)
                        dice, hd = utils.dice(cont1, cont2), utils.hausdorff(cont1, cont2)
                        rows.append([conttype, dice, hd])
                    except Exception as e: print(eva1.name, d, e)
        df = DataFrame(rows, columns=['Contour Type', 'Dice', 'HD'])
        ax.set_title('Dice (by slice & segmented by both)', fontsize=titlesize)
        dicebp = sns.boxplot(ax=ax, x="Contour Type", y="Dice", data=df, palette=custom_palette, width=0.8)
        sns.swarmplot(ax=ax, x="Contour Type", y="Dice", data=df, palette=swarm_palette)#, dodge=True)
        ax.set_ylabel('Dice [%]', fontsize=labelsize)
        ax.set_xlabel("", fontsize=labelsize)
        ymin = np.max([np.min(df['Dice']) - 5, 0])
        ax.set_ylim(ymin=ymin, ymax=101)
        
        # HD Values
        ax = axes[3][1]
        ax.set_title('Hausdorff (by slice & segmented by both)', fontsize=titlesize)
        dicebp = sns.boxplot(ax=ax, x="Contour Type", y="HD", data=df, palette=custom_palette, width=0.8)
        sns.swarmplot(ax=ax, x="Contour Type", y="HD", data=df, palette=swarm_palette)#, dodge=True)
        ax.set_ylabel('HD [mm]', fontsize=labelsize)
        ax.set_xlabel("", fontsize=labelsize)
        ymax = np.max(df['HD']) + 2
        ax.set_ylim(ymin=0, ymax=ymax)
        
        for ax_ in axes:
            for ax in ax_: ax.tick_params(axis='both', which='major', labelsize=ticksize)
        
        sns.despine()
        self.subplots_adjust(left=0.075, bottom=0.05, right=0.95, top=0.95, wspace=0.15, hspace=0.25)
    
    def store(self, storepath, figurename='clinical_results_bland_altman.png'):
        self.savefig(os.path.join(storepath, figurename), dpi=100, facecolor="#FFFFFF")
        return os.path.join(storepath, figurename)