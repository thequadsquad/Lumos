import pandas
from pandas import DataFrame
import traceback
import inspect

from Lumos.Tables.Table import *
from Lumos.loading_functions import *
from Lumos import ClinicalResults

import numpy as np


class Cases_Characteristics(Table):
    def calculate(self, cases):
        """Presents Clinical Results for the case_comparisons
        
        Note:
            Columns of mean±std for reader 1, reader 2, difference(reader1, reader2)
        
        Args:
            case_comparisons (list of Lumos.Containers.Case_Comparison): List of Case_Comparisons of two cases after View.customize_case(case) (for any View)
        """
        rows  = []
        evals = sorted(cases, key=lambda c: c.name)
        columns = ['Patient Name','Age','Sex','Height','Weight']
        
        for c in cases: 
            rows.append([c.name, c.age, c.gender, c.height, c.weight])
        self.df = DataFrame(rows, columns=columns)
        