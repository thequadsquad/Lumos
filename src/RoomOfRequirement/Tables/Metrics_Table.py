import pandas
from pandas import DataFrame
import traceback

from RoomOfRequirement.Tables.Table import *
from RoomOfRequirement.loading_functions import *
from RoomOfRequirement.Metrics import *



class Metrics_Table(Table):
    def _is_apic_midv_basal_outside(self, eva, d, p, cont_name):
        anno = eva.get_anno(d, p)
        has_cont = anno.has_contour(cont_name)
        if not has_cont:                    return 'outside'
        if has_cont and d==0:               return 'basal'
        if has_cont and d==eva.nr_slices-1: return 'apical'
        prev_has_cont = eva.get_anno(d-1, p).has_contour(cont_name)
        next_has_cont = eva.get_anno(d+1, p).has_contour(cont_name)
        if prev_has_cont and next_has_cont: return 'midv'
        if prev_has_cont and not next_has_cont: return 'apical'
        if not prev_has_cont and next_has_cont: return 'basal'
        
    
    def calculate(self, view, contname, p1, p2, eval1, eval2, pretty=True):
        """Presents table of Metric values for a Case_Comparison in SAX View
        
        Args:
            view (LazyLuna.Views.View): a view for the analysis
            cc (LazyLuna.Containers.Case_Comparison): contains two comparable cases
            contname (str): contour type to analyze
            pretty (bool): if True casts metric values to strings with two decimal places
        """
        mlDiff_m, dsc_m, hd_m, areadiff_m = mlDiffMetric(), DiceMetric(), HausdorffMetric(), AreaDiffMetric()
        eval1, eval2 = eval1, eval2
        rows, cols = [], []
        for d in range(eval1.nr_slices):
            try:
                dcm          = eval1.get_dcm(d, p1)
                anno1, anno2 = eval1.get_anno(d, p1), eval2.get_anno(d, p2)
                cont1, cont2 = anno1.get_contour(contname), anno2.get_contour(contname)
                ml_diff      = mlDiff_m.get_val(cont1, cont2, dcm, string=pretty)
                area_diff    = areadiff_m.get_val(cont1, cont2, dcm, string=pretty)
                dsc          = dsc_m.get_val(cont1, cont2, dcm, string=pretty)
                hd           = hd_m.get_val(cont1, cont2, dcm, string=pretty)
                pos1         = self._is_apic_midv_basal_outside(eval1, d, p1, contname)
                pos2         = self._is_apic_midv_basal_outside(eval2, d, p2, contname)
                has_cont1, has_cont2 = anno1.has_contour(contname), anno2.has_contour(contname)
                row = [ml_diff, area_diff, dsc, hd, pos1, pos2, has_cont1, has_cont2]
            except Exception as e: row.extend([np.nan for _ in range(8)]); print(traceback.format_exc())
            rows.append(row)
        #cols = self.resort(self.get_column_names(view, case1, contname), cats1)
        self.df = DataFrame(rows, columns=['ml Diff', 'Area Diff', 'DSC', 'HD', 'Pos1', 'Pos2', 'hascont1', 'hascont2'])
        
        