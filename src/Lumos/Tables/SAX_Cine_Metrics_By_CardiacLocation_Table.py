import pandas
from pandas import DataFrame
import traceback

from Lumos.loading_functions import *
from Lumos.Metrics import *

from Lumos.Tables.Table import *
from Lumos.Tables.CC_CRTable import *
from Lumos.Tables.SAX_CINE_CCs_Metrics_Table import *




class SAX_Cine_Metrics_By_CardiacLocation_Table(Table):
    def get_cardiac_location(self, eva, contname, phase):
        annos     = [eva.get_anno(d, phase) for d in range(eva.nr_slices)]
        has_conts = [a.has_contour(contname) if a is not None else 0.0 for a in annos]
        if True not in has_conts: return None
        base_idx = has_conts.index(True)
        apex_idx = eva.nr_slices - has_conts[::-1].index(True) - 1
        card_loc = ['outside base' if d<base_idx else 'outside apex' if d>apex_idx else 'base' if d==base_idx else 'apex' if d==apex_idx else 'midv' for d in range(eva.nr_slices)]
        return card_loc
            
    def calculate(self, view, evals1, evals2):
        """
        Presents informative table (combination of CRs and Metric values) for a list of Case_Comparisons
        
        Args:
            case_comparisons (list of LazyLuna.Containers.Case_Comparison): contains a list of case comparisons
            view (LazyLuna.Views.View): a view for the analysis
        """
        # # # First reader defines basal, midv, apical
        # Instantiate dictionaries
        dices, dices_both, hds, absmldiffs = dict(), dict(), dict(), dict()
        dice_m, hd_m, absmldiff_m = DiceMetric(), HausdorffMetric(), absMlDiffMetric()
        for cname in ['lv_endo', 'lv_myo', 'rv_endo']: 
            for cardiac_structure in ['base', 'midv', 'apex']:
                dices     [cname + ' ' + cardiac_structure] = []
                dices_both[cname + ' ' + cardiac_structure] = []
                hds       [cname + ' ' + cardiac_structure] = []
                absmldiffs[cname + ' ' + cardiac_structure] = []
        # calculate metric values
        for eva1,eva2 in zip(evals1, evals2):
            dcm = eva1.get_dcm(0,0)
            for cname in ['lv_endo', 'lv_myo', 'rv_endo']: 
                phases = view.clinical_phases[cname]
                phases = [view.clinical_parameters[p] for p in phases]
                for p1,p2 in [(p.get_val(eva1), p.get_val(eva2)) for p in phases]:
                    if np.isnan(p1) or np.isnan(p2): continue
                    card_loc = self.get_cardiac_location(eva1, cname, p1)
                    for d in range(eva1.nr_slices):
                        anno1, anno2 = eva1.get_anno(d,p1), eva2.get_anno(d,p2)
                        if not anno1.has_contour(cname) and not anno2.has_contour(cname): continue
                        cont1, cont2 = anno1.get_contour(cname), anno2.get_contour(cname)
                        cloc = card_loc[d].split(' ')[-1]
                        dices[cname+' '+cloc].append(dice_m.get_val(cont1, cont2))
                        if anno1.has_contour(cname) and anno2.has_contour(cname): 
                            dices_both[cname+' '+cloc].append(dice_m.get_val(cont1, cont2))
                        hds[cname+' '+cloc].append(hd_m.get_val(cont1, cont2,dcm=dcm))
                        absmldiffs[cname+' '+cloc].append(absmldiff_m.get_val(cont1, cont2,dcm=dcm))
        # make dataframe
        rows = []
        for card_loc in ['base', 'midv', 'apex']:
            rows.append([card_loc.capitalize(), '', '', ''])
            rows.append(['Dice [%]']+[np.nanmean(dices     [cname+' '+card_loc]) for cname in ['lv_endo', 'lv_myo', 'rv_endo']])
            rows.append(['Dice (segmented by both) [%]']+
                        [np.nanmean(dices_both[cname+' '+card_loc]) for cname in ['lv_endo', 'lv_myo', 'rv_endo']])
            rows.append(['HD [mm]']+[np.nanmean(hds       [cname+' '+card_loc]) for cname in ['lv_endo', 'lv_myo', 'rv_endo']])
            rows.append(['Abs. ml. diff [ml]']+
                        [np.nanmean(absmldiffs[cname+' '+card_loc]) for cname in ['lv_endo', 'lv_myo', 'rv_endo']])
        self.df = DataFrame(rows, columns=['Metric', 'LV Endo', 'LV Myo', 'RV Endo'])
        