import pandas
from pandas import DataFrame
import traceback

from RoomOfRequirement.Tables.Table import *
from RoomOfRequirement.loading_functions import *
from RoomOfRequirement.Metrics import *


class Metrics_Overview_Table(Table):
    def both_have_conts(self, hascont1, hascont2):
        if hascont1 and hascont2: return 'yes'
        else: return 'no'

    
    def calculate(self, view, contname, evals1, evals2, pretty=True):
        """Presents table of Metric values for a Case_Comparison in LGE SAX View                                                                       
        
        Args:
            view (LazyLuna.Views.View):      a view for the analysis (needs to be LGE sax)
            contname (str):                  contour type to analyze
            evals1, evals2 (LazyLuna.evals): evaluations for 2 tasks for all cases 
            pretty (bool):                   if True casts metric values to strings with two decimal places
        """
        
        eval1, eval2 = evals1[0], evals2[0]
        task1, task2 = eval1.taskname, eval2.taskname
        
        p1, p2 = 0,0
        if contname == 'lv_scar':
            dsc_m, areadiff_m, threshdiff_m, avgareaperthresh_m = DiceMetric(), AreaDiffMetric(), ThreshDiffMetric(), AvgAreaPerThreshMetric() 
            rows, cols = [], ['Case Name and compared tasks', 'Slice Nr', 'both have contours', 'Area Diff', 'DSC', 'Thresh Diff', 'Avg Area per Threshstep']
            
            for eval1 in evals1:
                for eval2 in evals2:
                    if eval1.name==eval2.name:
                        for d in range(eval1.nr_slices):
                            try:
                                dcm          = eval1.get_dcm(d, p1)
                                anno1, anno2 = eval1.get_anno(d, p1), eval2.get_anno(d, p2)
                                cont1, cont2 = anno1.get_contour(contname), anno2.get_contour(contname)
            
                                has_cont1, has_cont2 = anno1.has_contour(contname), anno2.has_contour(contname)
                                bhc = self.both_have_conts(has_cont1, has_cont2)
                                
                                area_diff    = areadiff_m.get_val(cont1, cont2, dcm, string=pretty)
                                dsc          = dsc_m.get_val(cont1, cont2, dcm, string=pretty)
                                threshdiff   = threshdiff_m.get_val(eval1, eval2, d, p1, p2, string=pretty)      
                                avgareaperthresh = avgareaperthresh_m.get_val(eval1, eval2, d, p1, p2, dcm, string=pretty)
                                
                                row = [eval1.name +': '+ task1 + ' & ' + task2, d, bhc, area_diff, dsc, threshdiff, avgareaperthresh]
                                rows.append(row)
                            except Exception as e:  print(traceback.format_exc()) 
                        
            self.df = DataFrame(rows, columns = cols).round(2)
            self.df_original = DataFrame(rows, columns = cols)
        else:
            dsc_m, areadiff_m = DiceMetric(), AreaDiffMetric()
            rows, cols = [], ['Case Name and compared tasks', 'Slice Nr', 'both have contours', 'Area Diff', 'DSC']
            for eval1 in evals1:
                for eval2 in evals2:
                    #print(eval1.name, eval2.name)
                    if eval1.name==eval2.name:
                        for d in range(eval1.nr_slices):
                            try:
                                dcm          = eval1.get_dcm(d, p1)
                                anno1, anno2 = eval1.get_anno(d, p1), eval2.get_anno(d, p2)
                                cont1, cont2 = anno1.get_contour(contname), anno2.get_contour(contname)
            
                                has_cont1, has_cont2 = anno1.has_contour(contname), anno2.has_contour(contname)
                                bhc = self.both_have_conts(has_cont1, has_cont2)
        
                                #print(cont1, cont2)
                                #print(dcm.PatientName)
        
                                #print(d, p1,p2)
                                
                                area_diff    = areadiff_m.get_val(cont1, cont2, dcm, string=pretty)
                                dsc          = dsc_m.get_val(cont1, cont2, dcm, string=pretty)
                                
                                row = [eval1.name +': '+ task1 + ' & ' + task2, d, bhc, area_diff, dsc]
                                rows.append(row)
                                
                            except Exception as e:  print(traceback.format_exc())  
                                
            self.df = DataFrame(rows, columns = cols).round(2)
            self.df_original = DataFrame(rows, columns = cols)

        
    def store(self):
        # selecting file path
        storepath, _ = QFileDialog.getSaveFileName(self, "Save Table", "",
                         "CSV(*.csv);;All Files(*.*) ")
 
        # if file path is blank return back
        if storepath == "":
            return
        #"""overwrite this function to store the Table's pandas.DataFrame (.df)"""
        pandas.DataFrame.to_csv(self.df_original, storepath, sep=';', decimal=',')
        

        


    




