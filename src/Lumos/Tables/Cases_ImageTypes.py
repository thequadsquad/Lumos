import pandas
from pandas import DataFrame
import traceback
import inspect

from Lumos.Tables.Table import *
from Lumos.loading_functions import *
from Lumos import ClinicalResults
from Lumos.ImageOrganizer import *

import numpy as np


class Cases_ImageTypes(Table):
    def calculate(self, cases):
        """Presents Clinical Results for the case_comparisons
        
        Note:
            Columns of mean±std for reader 1, reader 2, difference(reader1, reader2)
        
        Args:
            case_comparisons (list of Lumos.Containers.Case_Comparison): List of Case_Comparisons of two cases after View.customize_case(case) (for any View)
        """
        rows    = []

        quad = cases[0].db
        imgo_dicts = quad.imgo_coll.find({'studyuid' : {'$in': [c.studyuid for c in cases]}})
        imgos = [ImageOrganizer(quad, studyuid=imgod['studyuid'], imagetype=imgod['imagetype']) for imgod in imgo_dicts]
        
        imgos   = sorted(imgos, key=lambda e: (e.name, e.imagetype))
        all_imgtypes = sorted(list(set([i.imagetype for i in imgos])))
        columns = ['Patient Name','Age','Sex','Height','Weight']+all_imgtypes

        cases = sorted(list(set([(c.studyuid,c.name,c.age,c.gender,c.height,c.weight) for c in cases])), key=lambda x: x[1])
        suid2imgtypes = {c[0]:[] for c in cases}
        for imgo in imgos: suid2imgtypes[imgo.studyuid].append(imgo.imagetype)

        for c in cases:
            row = [c[1],c[2],c[3],c[4],c[5]]
            for imgtype in all_imgtypes:
                if imgtype in suid2imgtypes[c[0]]: row.append(True)
                else:                              row.append(False)
            rows.append(row)
        
        self.df = DataFrame(rows, columns=columns)


