import pandas
from pandas import DataFrame
import traceback

from RoomOfRequirement.loading_functions import *
from RoomOfRequirement.Metrics import *

from RoomOfRequirement.Tables.Table import *
from RoomOfRequirement.Tables.CC_CRTable import *
from RoomOfRequirement.Tables.SAX_CINE_CCs_Metrics_Table import *




class SAX_Cine_CCs_pretty_averageCRs_averageMetrics_Table(Table):
    def get_cp_diffs_table(self, view, evals1, evals2):
        cpnames = ['LVESV', 'LVEDV', 'LVSV', 'LVEF', 'LVM', 'RVESV', 'RVEDV', 'RVSV', 'RVEF']
        rows = []
        for eva1, eva2 in zip(evals1, evals2):
            rows.append([view.clinical_parameters[cpn].get_val_diff(eva1, eva2) for cpn in cpnames])
        return DataFrame(rows, columns=cpnames)
    
    def get_metrics_table(self, view, evals1, evals2):
        dices, dices_both, hds, absmldiffs = dict(), dict(), dict(), dict()
        dice_m, hd_m, absmldiff_m = DiceMetric(), HausdorffMetric(), absMlDiffMetric()
        for cname in ['lv_endo', 'lv_myo', 'rv_endo']: 
            dices[cname]=[]; dices_both[cname]=[]; hds[cname]=[]; absmldiffs[cname]=[]
        for eva1,eva2 in zip(evals1, evals2):
            dcm = eva1.get_dcm(0,0)
            for d in range(eva1.nr_slices):
                # get the phases
                esp, edp = view.clinical_phases['lv_endo']
                esp, edp = view.clinical_parameters[esp], view.clinical_parameters[edp]
                # p1,p2 in {es and ed}
                for p1,p2 in [(esp.get_val(eva1),esp.get_val(eva2)), (edp.get_val(eva1),edp.get_val(eva2))]:
                    try:
                        cont1, cont2 = eva1.get_anno(d,p1).get_contour('lv_endo'), eva2.get_anno(d,p2).get_contour('lv_endo')
                        dices['lv_endo'].append(dice_m.get_val(cont1, cont2))
                        if eva1.get_anno(d,p1).has_contour('lv_endo') and eva2.get_anno(d,p2).has_contour('lv_endo'):
                            dices_both['lv_endo'].append(dice_m.get_val(cont1, cont2))
                        hds['lv_endo'].append(hd_m.get_val(cont1, cont2,dcm=dcm))
                        absmldiffs['lv_endo'].append(absmldiff_m.get_val(cont1, cont2,dcm=dcm))
                    except Exception as e: continue; print(traceback.print_exc()); pass
                esp, edp = view.clinical_phases['rv_endo']
                esp, edp = view.clinical_parameters[esp], view.clinical_parameters[edp]
                # p1,p2 in {es and ed}
                for p1,p2 in [(esp.get_val(eva1),esp.get_val(eva2)), (edp.get_val(eva1),edp.get_val(eva2))]:
                    try:
                        cont1, cont2 = eva1.get_anno(d,p1).get_contour('rv_endo'), eva2.get_anno(d,p2).get_contour('rv_endo')
                        dices['rv_endo'].append(dice_m.get_val(cont1, cont2))
                        if eva1.get_anno(d,p1).has_contour('rv_endo') and eva2.get_anno(d,p2).has_contour('rv_endo'):
                            dices_both['rv_endo'].append(dice_m.get_val(cont1, cont2))
                        hds['rv_endo'].append(hd_m.get_val(cont1, cont2,dcm=dcm))
                        absmldiffs['rv_endo'].append(absmldiff_m.get_val(cont1, cont2,dcm=dcm))
                    except Exception as e: continue; print(traceback.print_exc()); pass
                # get the phases
                edp = view.clinical_phases['lv_myo'][0]
                edp = view.clinical_parameters[edp]
                # p1,p2 in {ed}
                for p1,p2 in [(edp.get_val(eva1),edp.get_val(eva2))]:
                    try:
                        cont1, cont2 = eva1.get_anno(d,p1).get_contour('lv_myo'), eva2.get_anno(d,p2).get_contour('lv_myo')
                        dices['lv_myo'].append(dice_m.get_val(cont1, cont2))
                        if eva1.get_anno(d,p1).has_contour('lv_myo') and eva2.get_anno(d,p2).has_contour('lv_myo'):
                            dices_both['lv_myo'].append(dice_m.get_val(cont1, cont2))
                        hds['lv_myo'].append(hd_m.get_val(cont1, cont2,dcm=dcm))
                        absmldiffs['lv_myo'].append(absmldiff_m.get_val(cont1, cont2,dcm=dcm))
                    except Exception as e: continue; print(traceback.print_exc()); pass
        rows = [['Dice [%]',                     'LV Endo', np.nanmean(dices['lv_endo']),      np.nanstd(dices['lv_endo'])],
                ['Dice (segmented by both) [%]', 'LV Endo', np.nanmean(dices_both['lv_endo']), np.nanstd(dices_both['lv_endo'])],
                ['Hausdorff [mm]',               'LV Endo', np.nanmean(hds['lv_endo']),        np.nanstd(hds['lv_endo'])],
                ['Abs. ml. diff. [ml]',          'LV Endo', np.nanmean(hds['lv_endo']),        np.nanstd(hds['lv_endo'])],
                
                ['Dice [%]',                     'RV Endo', np.nanmean(dices['rv_endo']),     np.nanstd(dices['rv_endo'])],
                ['Dice (segmented by both) [%]', 'RV Endo', np.nanmean(dices_both['rv_endo']),np.nanstd(dices_both['rv_endo'])],
                ['Hausdorff [mm]',               'RV Endo', np.nanmean(hds['rv_endo']),       np.nanstd(hds['rv_endo'])],
                ['Abs. ml. diff. [ml]',          'RV Endo', np.nanmean(hds['rv_endo']),       np.nanstd(hds['rv_endo'])],
                
                ['Dice [%]',                     'LV Myo', np.nanmean(dices['lv_myo']),      np.nanstd(dices['lv_myo'])],
                ['Dice (segmented by both) [%]', 'LV Myo', np.nanmean(dices_both['lv_myo']), np.nanstd(dices_both['lv_myo'])],
                ['Hausdorff [mm]',               'LV Myo', np.nanmean(hds['lv_myo']),        np.nanstd(hds['lv_myo'])],
                ['Abs. ml. diff. [ml]',          'LV Myo', np.nanmean(hds['lv_myo']),        np.nanstd(hds['lv_myo'])]]
        df = DataFrame(rows, columns=['Metric', 'Contour Type', 'Average', 'Standard Deviation'])
        return df
    
    def calculate(self, view, evals1, evals2):
        """
        Presents informative table (combination of CRs and Metric values) for a list of Case_Comparisons
        
        Args:
            case_comparisons (list of LazyLuna.Containers.Case_Comparison): contains a list of case comparisons
            view (LazyLuna.Views.View): a view for the analysis
        """
        cp_table = self.get_cp_diffs_table(view, evals1, evals2)
        cp_avgs  = cp_table.mean(axis=0).to_dict()
        cp_stds  = cp_table.std(axis=0) .to_dict()
        metric_table = self.get_metrics_table (view, evals1, evals2)
        
        rows = []
        for k in cp_avgs.keys():
            if not (k.startswith('LV') and k!='LVM'): continue
            cp = view.clinical_parameters[k]
            rows.append([cp.name+' '+cp.unit, cp_avgs[k], cp_stds[k]])
        lv_endo_metric_rows = metric_table[metric_table['Contour Type']=='LV Endo'].values.tolist()
        for row in lv_endo_metric_rows: rows.append(['    ('+row[1]+') '+row[0], row[2], row[3]])
        for k in cp_avgs.keys():
            if not k=='LVM': continue 
            cp = view.clinical_parameters[k]
            rows.append([cp.name+' '+cp.unit, cp_avgs[k], cp_stds[k]])
        lv_endo_metric_rows = metric_table[metric_table['Contour Type']=='LV Myo'].values.tolist()
        for row in lv_endo_metric_rows: rows.append(['    ('+row[1]+') '+row[0], row[2], row[3]])
        for k in cp_avgs.keys():
            if not k.startswith('RV'): continue 
            cp = view.clinical_parameters[k]
            rows.append([cp.name+' '+cp.unit, cp_avgs[k], cp_stds[k]])
        lv_endo_metric_rows = metric_table[metric_table['Contour Type']=='RV Endo'].values.tolist()
        for row in lv_endo_metric_rows: rows.append(['    ('+row[1]+') '+row[0], row[2], row[3]])
        
        self.df = DataFrame(rows, columns=['Parameter [unit]', 'Average', 'Standard Deviation'])
        
        

"""
class SAX_Cine_CCs_pretty_averageCRs_averageMetrics_Table(Table):
    def calculate(self, view, evals1, evals2):
        cr_table = CCs_ClinicalResultsTable()
        cr_table.calculate(case_comparisons, with_metrics=True)
        means_cr_table = cr_table.df[['LVEF difference', 'LVEDV difference', 'LVESV difference', 'lv_endo avg dice', 
                             'lv_endo avg dice cont by both', 'lv_endo avg HD', 'LVM difference', 'lv_myo avg dice', 
                            'lv_myo avg dice cont by both', 'lv_myo avg HD', 'RVEF difference', 'RVEDV difference', 
                            'RVESV difference', 'rv_endo avg dice', 'rv_endo avg dice cont by both', 'rv_endo avg HD', 
                            'avg dice', 'avg dice cont by both', 'avg HD']].mean(axis=0)
        std_cr_table = cr_table.df[['LVEF difference', 'LVEDV difference', 'LVESV difference', 'lv_endo avg dice', 
                             'lv_endo avg dice cont by both', 'lv_endo avg HD', 'LVM difference', 'lv_myo avg dice', 
                            'lv_myo avg dice cont by both', 'lv_myo avg HD', 'RVEF difference', 'RVEDV difference', 
                            'RVESV difference', 'rv_endo avg dice', 'rv_endo avg dice cont by both', 'rv_endo avg HD', 
                            'avg dice', 'avg dice cont by both', 'avg HD']].std(axis=0)
        cr_table = pandas.concat([means_cr_table, std_cr_table], axis=1).reset_index()
        cr_table.columns = ['Name', 'Mean', 'Std']
        names = cr_table['Name']
        new_names = []
        for i, n in names.iteritems():
            n = n.replace(' difference', '').replace('avg HD','HD').replace('avg dice', 'Dice').replace('lv_endo', '').replace('rv_endo', '').replace('lv_myo','')
            if 'cont by both' in n: n = n.replace('cont by both', '(slices contoured by both)')
            elif 'Dice' in n:       n = n + ' (all slices)'
            if i>15:                     n = n + ' (all contours)'
            n = n.replace(') (', ', ')
            if 'HD' in n:                n = n + ' [mm]'
            if 'EF' in n or 'Dice' in n: n = n + ' [%]'
            if 'ESV' in n or 'EDV' in n: n = n + ' [ml]'
            if 'LVM' in n:               n = n + ' [g]'
            new_names.append(n)
        cr_table['Name'] = new_names
        self.cr_table = cr_table
        
        metrics_table = SAX_CINE_CCs_Metrics_Table()
        metrics_table.calculate(view, case_comparisons, pretty=False)
        metrics_table = metrics_table.df
        
        rows = []
        for position in ['basal', 'midv', 'apical']:
            # Precision = tp / tp + fp
            # Recall    = tp / tp + fn
            # dice all slices
            # dice by both
            row1, row2 = [position, 'Dice (all slices) [%]'], [position, 'Dice (slices contoured by both) [%]']
            row3, row4 = [position, 'HD [mm]'], [position, 'Abs. ml diff. (per slice) [ml]']
            for contname in ['lv_endo', 'lv_myo', 'rv_endo']:
                subtable = metrics_table[[k for k in metrics_table.columns if contname in k]]
                dice_ks     = [k for k in subtable.columns if 'DSC' in k]
                position_ks = [k for k in subtable.columns if 'Pos1' in k]
                all_dices = []
                for ki in range(len(dice_ks)): 
                    all_dices.extend([d for d in subtable[subtable[position_ks[ki]]==position][dice_ks[ki]]])
                row1.append(np.nanmean(all_dices))
                row2.append(np.nanmean([d for d in all_dices if 0<d<100]))
                hd_ks = [k for k in subtable.columns if 'HD' in k]
                hds   = []
                for ki in range(len(hd_ks)): hds.extend([d for d in subtable[subtable[position_ks[ki]]==position][hd_ks[ki]]])
                row3.append(np.nanmean(hds))
                # abs ml diff
                mld_ks = [k for k in subtable.columns if 'Abs ml Diff' in k]
                mlds   = []
                for ki in range(len(mld_ks)): mlds.extend([d for d in subtable[subtable[position_ks[ki]]==position][mld_ks[ki]]])
                row4.append(np.nanmean(mlds))
            rows.extend([row1, row2, row3, row4])
        self.metrics_table = DataFrame(rows, columns=['Position', 'Metric', 'LV Endocardial Contour', 'LV Myocardial Contour', 'RV Endocardial Contour'])
        #display(self.metrics_table)
        
    def present_metrics(self):
        self.df = self.metrics_table
    
    def present_crs(self):
        self.df = self.cr_table
"""
        