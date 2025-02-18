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


        
class SAXCINE_Confidence_Intervals_Tolerance_Ranges(Visualization):
    def visualize(self, view, evals1, evals2, with_swarmplot=True):
        """Takes a list of case_comparisons and plots confidence intervals for Clinical Results
        
        Args:
            case_comparisons (list of LazyLuna.Containers.Case_Comparison): list of case comparisons for calculation
            with_swarmplot (bool): whether to plot CRs of the individual case comparisons on top of the confidence intervals
        """
        cpnames = ['LVESV', 'LVEDV', 'LVSV', 'LVEF', 'LVM', 'RVESV', 'RVEDV', 'RVSV', 'RVEF']
        cpname2values = {cpn:[] for cpn in cpnames}
        for eva1, eva2 in zip(evals1, evals2):
            for cpname in cpnames:
                cp = view.clinical_parameters[cpname]
                cpname2values[cpname].append(cp.get_val_diff(eva1, eva2))
        self.set_size_inches(w=15, h=15)
        axes = self.subplots(3,3)
        for ax_i in range(9):
            i, j = ax_i//3, ax_i%3
            ax = axes[i][j]
            try:
                name = cpnames[ax_i]
                cp = view.clinical_parameters[name]
                ax.set_title(name, fontsize=16)
                if np.isnan(np.nanmean(cpname2values[name])): ax.set_title('No '+name+' Values Available')
                ax.axhspan(-cp.tol_range, cp.tol_range, facecolor='0.6', alpha=0.5)
                alpha = 0.5 if with_swarmplot else 0.0
                ci = 1.96 * np.nanstd(cpname2values[name]) / np.sqrt(len(cpname2values[name]))
                sns.swarmplot(ax=ax, y=cpname2values[name], palette=sns.color_palette("Blues")[4:], 
                              dodge=True, size=5, alpha=alpha)
                sns.pointplot(ax=ax, y=cpname2values[name], errorbar=("ci", 95), color='r')
                maxx = np.max([np.abs(np.nanmin(cpname2values[name])), np.abs(np.nanmax(cpname2values[name])),
                               np.abs(np.nanmean(cpname2values[name])-ci), np.abs(np.nanmean(cpname2values[name])+ci), 
                               cp.tol_range])
                ax.set_ylim(ymin=-maxx-2, ymax=maxx+2)
                ax.set_ylabel(name + ' ' + cp.unit)
                ax.set_xlabel('')
                ax.tick_params(axis='both', which='major', labelsize=14)
            except: continue
        self.tight_layout()
    
    def store(self, storepath, figurename='confidence_intervals_tolerance_ranges.png'):
        self.savefig(os.path.join(storepath, figurename), dpi=300, facecolor="#FFFFFF")
        return os.path.join(storepath, figurename)