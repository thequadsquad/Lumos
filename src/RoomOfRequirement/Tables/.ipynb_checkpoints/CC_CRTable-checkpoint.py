import pandas
from pandas import DataFrame
import traceback
import inspect

from RoomOfRequirement.Tables.Table import *
from RoomOfRequirement.loading_functions import *
from RoomOfRequirement import ClinicalResults

import numpy as np


class CCs_ClinicalResultsTable(Table):
    def calculate(self, view, evals):
        """Presents Clinical Results for the case_comparisons
        
        Note:
            Columns of mean±std for reader 1, reader 2, difference(reader1, reader2)
        
        Args:
            case_comparisons (list of RoomOfRequirement.Containers.Case_Comparison): List of Case_Comparisons of two cases after View.customize_case(case) (for any View)
        """
        rows  = []
        evals = sorted(evals, key=lambda e: e.name)
        eval1 = evals[0]
        columns = ['Patient Name','Age','Sex','Height','Weight']+list([cr.name+' '+cr.unit for cr in view.clinical_parameters.values()])
        
        for eva in evals:
            row = [eva.name, eva.age, eva.sex, eva.size, eva.weight]
            for cr_name, cr in view.clinical_parameters.items():
                try:    cr = eva.clinical_parameters[cr_name][0]
                except: cr = np.nan
                row.append(cr)
            rows.append(row)
        self.df = DataFrame(rows, columns=columns)
        
    def calculate_diffs(self, view, evals1, evals2):
        """Presents Clinical Results for the case_comparisons
        
        Note:
            Columns of mean±std for reader 1, reader 2, difference(reader1, reader2)
        
        Args:
            case_comparisons (list of RoomOfRequirement.Containers.Case_Comparison): List of Case_Comparisons of two cases after View.customize_case(case) (for any View)
        """
        rows  = []
        evals1 = sorted(evals1, key=lambda e: e.name)
        evals2 = sorted(evals2, key=lambda e: e.name)
        eval1 = evals1[0]
        columns = ['Patient Name','Age','Sex','Height','Weight']+list([cr.name+' '+cr.unit for cr in view.clinical_parameters.values()])
        
        for eva1, eva2 in zip(evals1, evals2):
            row = [eva1.name, eva1.age, eva1.sex, eva1.size, eva1.weight]
            for cr_name, cr in view.clinical_parameters.items():
                try:
                    diff = cr.get_val_diff(eva1, eva2)
                except: 
                    diff = np.nan
                row.append(diff)
            rows.append(row)
        self.df = DataFrame(rows, columns=columns)
        
        