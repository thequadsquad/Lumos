import pandas
from pandas import DataFrame
import traceback

from RoomOfRequirement.Tables.Table import *
from RoomOfRequirement.loading_functions import *
from RoomOfRequirement.Metrics import *


class Clinical_Results_Overview_Table(Table):    
    def calculate(self, view, evals1, evals2, pretty=True):
        """Presents table of Metric values for a Case_Comparison in LGE SAX View                                                                       
        
        Args:
            view (LazyLuna.Views.View): a view for the analysis
            cc (LazyLuna.Containers.Case_Comparison): contains two comparable cases
            contname (str): contour type to analyze
            pretty (bool): if True casts metric values to strings with two decimal places
        """
        
        eval1, eval2 = evals1[0], evals2[0]
        
        cols, rows = ['Case Name'], [] 
        #scar_mass, myo_mass, scar_pct = 'SCAR_MASS', 'MYO_MASS', 'SCAR_PCT'
        
        for cp in eval1.clinical_parameters.keys():
            
            cols.append(eval1.taskname +': '+ cp + eval1.clinical_parameters[cp][1])
            cols.append(eval2.taskname +': '+ cp + eval2.clinical_parameters[cp][1])
        
        for eval1 in evals1:
            row = [eval1.name]
            for cp in eval1.clinical_parameters.keys():
                row.append(eval1.clinical_parameters[cp][0])
                for eval2 in evals2:
                    if eval2.name==eval1.name:     
                        row.append(eval2.clinical_parameters[cp][0])  
            rows.append(row)
        
        self.df = DataFrame(rows, columns=cols).round(2)
        self.df_original = DataFrame(rows, columns=cols)

        
    def store(self):
        # selecting file path
        storepath, _ = QFileDialog.getSaveFileName(self, "Save Table", "",
                         "CSV(*.csv);;All Files(*.*) ")
 
        # if file path is blank return back
        if storepath == "":
            return
        """overwrite this function to store the Table's pandas.DataFrame (.df)"""
        pandas.DataFrame.to_csv(self.df_original, storepath, sep=';', decimal=',')
        

        


    




