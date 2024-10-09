from PyQt6.QtWidgets import QFileDialog

import pandas
from pandas import DataFrame
import traceback
import inspect

from RoomOfRequirement.Tables.Table import *
from RoomOfRequirement.loading_functions import *
from RoomOfRequirement import ClinicalResults

import numpy as np


class Multi_ClinicalResultsAveragesTable(Table):
    def calculate(self, view, evals_list):
        """Presents Clinical Results for the case_comparisons
        
        Note:
            Columns of mean±std for reader 1, reader 2, ...
        
        Args:
            view
            evals_list
        """
        
        rows = []
        eval_dict = dict()
        for i in range(0, len(evals_list)):
            eval_dict[i] = evals_list[i][0]

        columns = ['Clinical Result (mean±std)'] 
        for i in range(0, len(evals_list)):
            columns.append(eval_dict[i].taskname) 
        crs = view.clinical_parameters.items()
        
        cr_dict = dict()
        for i in range(0, len(evals_list)):
            cr_dict[i] = {view.clinical_parameters[cr_name].name+' '+view.clinical_parameters[cr_name].unit:[] for cr_name, cr in crs}
        
        for i in range(0, len(evals_list)):
            for eval in evals_list[i]:
                for cr_name, cr in view.clinical_parameters.items():
                    print(cr_name, cr)
                    try:
                        cr = eval.clinical_parameters[cr_name]
                        cr_dict[i][view.clinical_parameters[cr_name].name+' '+view.clinical_parameters[cr_name].unit].append(cr[0])
                        
                    except:
                        print(traceback.format_exc())
                        continue
        rows = []
        for cr_name in cr_dict[0].keys():
            row = [cr_name]
            for i in range(0, len(evals_list)):
                row.append('{:.1f}'.format(np.nanmean(cr_dict[i][cr_name])) + ' (' +'{:.1f}'.format(np.nanstd(cr_dict[i][cr_name])) + ')')
            rows.append(row)
        self.df = DataFrame(rows, columns=columns)
        
        
        