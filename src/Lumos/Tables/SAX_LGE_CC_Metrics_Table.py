import pandas
from pandas import DataFrame
import traceback

from Lumos.Tables.Table import *
from Lumos.loading_functions import *
from Lumos.Metrics import *



class SAX_LGE_CC_Metrics_Table(Table):                                                                                      
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
        

    '''
    def get_thresh(self, geo, dcm, string=False):
        """returns thresh (lowest pixelintensity in geos)

        Args:
            geo (shapely.geometry) : contour object 
            dcm (dicom dataset):     dicom dataset with pixel spacing and slice thickness
            string (bool):           return string of float with 2 decimal places 
            
        Returns:
            float | str: Number Threshold 
        """
        mask                 = utils.to_mask_pct(geo, dcm.Columns, dcm.Rows)
        intensity_values     = np.ravel(np.where(mask !=0, dcm.pixel_array, 0))
        #mask_myo             = utils.to_mask_pct(geo_myo, dcm.Columns, dcm.Rows)
        #intensity_values_myo = np.ravel(np.where(mask_myo !=0, dcm.pixel_array, 0))
        try:
            thresh = min(i for i in intensity_values if i > 0)
        except:
            thresh = np.nan #max(i for i in intensity_values_myo)                       
        return "{:.2f}".format(thresh) if string else thresh
    '''

    
    def calculate(self, view, contname, p1, p2, eval1, eval2, pretty=True):
        """Presents table of Metric values for a Case_Comparison in LGE SAX View                                                                       
        
        Args:
            view (LazyLuna.Views.View): a view for the analysis
            cc (LazyLuna.Containers.Case_Comparison): contains two comparable cases
            contname (str): contour type to analyze
            pretty (bool): if True casts metric values to strings with two decimal places
        """
        mlDiff_m, dsc_m, hd_m, areadiff_m, threshdiff_m, avgareaperthresh_m = mlDiffMetric(), DiceMetric(), HausdorffMetric(), AreaDiffMetric(), ThreshDiffMetric(), AvgAreaPerThreshMetric()         #hier threshdiff_m = ThreshDiffMetric() hinzugefügt
        eval1, eval2 = eval1, eval2
        rows, cols = [], []
        if contname == 'lv_scar':
            for d in range(eval1.nr_slices):
                try:
                    dcm          = eval1.get_dcm(d, p1)
                    anno1, anno2 = eval1.get_anno(d, p1), eval2.get_anno(d, p2)
                    cont1, cont2 = anno1.get_contour(contname), anno2.get_contour(contname)
                    ml_diff      = mlDiff_m.get_val(cont1, cont2, dcm, string=pretty)
                    area_diff    = areadiff_m.get_val(cont1, cont2, dcm, string=pretty)
                    dsc          = dsc_m.get_val(cont1, cont2, dcm, string=pretty)
                    hd           = hd_m.get_val(cont1, cont2, dcm, string=pretty)
                    threshdiff   = threshdiff_m.get_val(eval1, eval2, d, p1, p2, string=pretty)      #p1 und p2 für LGe immer gleich?
                    avgareaperthresh = avgareaperthresh_m.get_val(eval1, eval2, d, p1, p2, dcm, string=pretty)
                    thresh1      = eval1.get_threshold(d, p1, string=pretty)
                    thresh2      = eval2.get_threshold(d, p2, string=pretty)
                    #thresh1      = self.get_thresh(cont1, dcm, string=pretty)
                    #thresh2      = self.get_thresh(cont2, dcm, string=pretty)
                    pos1         = self._is_apic_midv_basal_outside(eval1, d, p1, contname)
                    pos2         = self._is_apic_midv_basal_outside(eval2, d, p2, contname)
                    has_cont1, has_cont2 = anno1.has_contour(contname), anno2.has_contour(contname)
                    row = [ml_diff, area_diff, dsc, hd, threshdiff, avgareaperthresh, thresh1, thresh2, pos1, pos2, has_cont1, has_cont2]                                                           #hier thresh_diff, thresh1, thresh2 hinzugefügt
                except Exception as e: row.extend([np.nan for _ in range(12)]); print(traceback.format_exc())                                                                     #hier range(11) statt range(8)/range(9)
                rows.append(row)
            #cols = self.resort(self.get_column_names(view, case1, contname), cats1)
            self.df = DataFrame(rows, columns=['ml Diff', 'Area Diff', 'DSC', 'HD', 'Thresh Diff', 'Avg Area per Threshstep', 'Thresh1', 'Thresh2', 'Pos1', 'Pos2', 'hascont1', 'hascont2'])                 #hier 'Thresh Diff' hinzugefügt  
        else:
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
                    row = [ml_diff, area_diff, dsc, hd, pos1, pos2, has_cont1, has_cont2]                                                           #hier thresh_diff, thresh1, thresh2 hinzugefügt
                except Exception as e: row.extend([np.nan for _ in range(8)]); print(traceback.format_exc())                                                                     #hier range(11) statt range(8)/range(9)
                rows.append(row)
            #cols = self.resort(self.get_column_names(view, case1, contname), cats1)
            self.df = DataFrame(rows, columns=['ml Diff', 'Area Diff', 'DSC', 'HD', 'Pos1', 'Pos2', 'hascont1', 'hascont2'])                 #hier 'Thresh Diff' hinzugefügt  


    
