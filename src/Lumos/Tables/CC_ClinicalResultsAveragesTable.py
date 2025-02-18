import pandas
from pandas import DataFrame
import traceback
import inspect

from Lumos.Tables.Table import *
from Lumos.loading_functions import *
from Lumos import ClinicalResults

import numpy as np


class CC_ClinicalResultsAveragesTable(Table):
    def calculate(self, view, evals1, evals2):
        """Presents Clinical Results for the case_comparisons
        
        Note:
            Columns of mean±std for reader 1, reader 2, difference(reader1, reader2)
        
        Args:
            case_comparisons (list of Lumos.Containers.Case_Comparison): List of Case_Comparisons of two cases after View.customize_case(case) (for any View)
        """
        
        rows = []
        eval1, eval2 = evals1[0], evals2[0]
        #columns=['Clinical Result (mean±std)', case1.reader_name, case2.reader_name, 'Diff('+case1.reader_name+', '+case2.reader_name+')', '(Mean Diff±CI), ±Tol range']
        columns=['Clinical Result (mean±std)', eval1.taskname, eval2.taskname, 'Difference', 'Tolerance range']
        
        crs = view.clinical_parameters.values()
        cr_dict1 = {cr.name+' '+cr.unit:[] for cr in crs}
        cr_dict2 = {cr.name+' '+cr.unit:[] for cr in crs}
        cr_dict3 = {cr.name+' '+cr.unit:[] for cr in crs}
        cr_tolrange_dict = {cr.name+' '+cr.unit: cr.tol_range if hasattr(cr, 'tol_range') else np.nan for cr in crs}
        for eval1, eval2 in zip(evals1, evals2):
            #for k in set(eval1.clinical_parameters.keys()).intersection(set(eval2.clinical_parameters.keys())):
            for cr_name, cr in view.clinical_parameters.items():
                print(cr_name, cr)
                try:
                    cr1, cr2 = eval1.clinical_parameters[cr_name], eval2.clinical_parameters[cr_name]
                    cr_dict1[cr_name+' '+cr.unit].append(cr1[0])
                    cr_dict2[cr_name+' '+cr.unit].append(cr2[0])
                    cr_dict3[cr_name+' '+cr.unit].append(cr.get_val_diff(eval1, eval2))
                except:
                    print(traceback.format_exc())
                    continue
        rows = []
        for cr_name in cr_dict1.keys():
            row = [cr_name]
            row.append('{:.1f}'.format(np.nanmean(cr_dict1[cr_name])) + ' (' +'{:.1f}'.format(np.nanstd(cr_dict1[cr_name])) + ')')
            row.append('{:.1f}'.format(np.nanmean(cr_dict2[cr_name])) + ' (' +'{:.1f}'.format(np.nanstd(cr_dict2[cr_name])) + ')')
            row.append('{:.1f}'.format(np.nanmean(cr_dict3[cr_name])) + ' (' +'{:.1f}'.format(np.nanstd(cr_dict3[cr_name])) + ')')
            mean = np.nanmean(cr_dict3[cr_name])
            ci   = 1.96 * np.nanstd(cr_dict3[cr_name]) / np.sqrt(len(cr_dict3[cr_name]))
            row.append('({:.1f}'.format(mean-ci) + ', {:.1f}'.format(mean+ci)+ '), ±{:.1f}'.format(cr_tolrange_dict[cr_name]))
            rows.append(row)
        self.df = DataFrame(rows, columns=columns)
        
        