import pandas
from pandas import DataFrame
import traceback
import inspect

from RoomOfRequirement.Tables.Table import *
from RoomOfRequirement.loading_functions import *
from RoomOfRequirement import ClinicalResults
from RoomOfRequirement.ImageOrganizer import *
from RoomOfRequirement.Evaluation import *

import numpy as np


class Cases_AvailableAnnotypes(Table):
    def calculate(self, cases, task_id):
        """Presents Clinical Results for the case_comparisons
        
        Note:
            Columns of mean±std for reader 1, reader 2, difference(reader1, reader2)
        
        Args:
            case_comparisons (list of RoomOfRequirement.Containers.Case_Comparison): List of Case_Comparisons of two cases after View.customize_case(case) (for any View)
        """
        rows       = []
        quad       = cases[0].db
        imgo_dicts = quad.imgo_coll.find({'studyuid' : {'$in': [c.studyuid for c in cases]}})
        imgos      = [ImageOrganizer(quad, studyuid=imgod['studyuid'], imagetype=imgod['imagetype']) for imgod in imgo_dicts]
        
        imgos        = sorted(imgos, key=lambda e: (e.name, e.imagetype))
        all_imgtypes = sorted(list(set([i.imagetype for i in imgos])))
        columns      = ['Patient Name','Age','Sex','Height','Weight'] + all_imgtypes

        eval_dicts = quad.eval_coll.find({'studyuid' : {'$in': [c.studyuid for c in cases]}, 'task_id': task_id})
        evals      = [Evaluation(quad, studyuid=eva['studyuid'], imagetype=eva['imagetype'], task_id=task_id) for eva in eval_dicts]
        
        cases                = sorted(list(set([(c.studyuid,c.name,c.age,c.gender,c.height,c.weight) for c in cases])), key=lambda x: x[1])
        suid2imgt2availannos = {suid:{it: False} for suid in [c[0] for c in cases] for it in all_imgtypes}
        suid2imgt2availannos = {suid:{} for suid in [c[0] for c in cases]}
        for suid in suid2imgt2availannos.keys(): 
            for it in all_imgtypes: 
                suid2imgt2availannos[suid][it]=False
        for eva in evals:
            suid2imgt2availannos[eva.studyuid][eva.imagetype] = sorted(eva.available_contours)
        print(suid2imgt2availannos)

        for c in cases:
            row = [c[1],c[2],c[3],c[4],c[5]]
            for imgtype in all_imgtypes: 
                row.append(suid2imgt2availannos[c[0]][imgtype])
            rows.append(row)
            
        self.df = DataFrame(rows, columns=columns)


