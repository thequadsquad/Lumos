from Lumos.Views import *
from Lumos.ImageOrganizer import *
from Lumos.Evaluation import *

import pydicom

import copy

# Keep generic: 
# - case can have a reader and a studyuid (with images and evals)
# - case can refer to a study with images without a reader (without evals)
# - case can refer to a study without images but with evaluations (e.g. imported cvi reports)

class Case:
    def __init__(self, db, studyuid=None):
        if studyuid is not None: 
            try: self.__dict__ = db.case_coll.find_one({'studyuid': studyuid})
            except Exception as e: pass
        self.db = db
        self.studyuid = studyuid
        self.name, self.age, self.gender, self.weight, self.height = self.get_patient_info()
        
    def get_imgo(self, viewname):
        return self.imgos(viewname)
    
    def get_eval(self, viewname):
        return self.evals(viewname)
    
    def get_patient_info(self):
        dcm  = pydicom.dcmread(self.db.dcm_coll.find_one({'studyuid' : self.studyuid})['path'], stop_before_pixels=True)
        info = []
        try:    info.append(str(dcm.PatientName))
        except: info.append('')
        try:    info.append(str(dcm.PatientAge))
        except: info.append('')
        try:    info.append(str(dcm.PatientSex))
        except: info.append('')
        try:    info.append(str(dcm.PatientWeight))
        except: info.append('')
        try:    info.append(str(dcm.PatientSize))
        except: info.append('')
        return info

    
    ########################################
    ## add valuable information to cases  ##
    ########################################
    def set_primary_disease(self, disease):
        self.primary_disease = disease
        
    def set_same_persons(self, other_studyuids):
        self.same_persons = list(set(other_studyuids))
    
    def set_duplicate_images(self, other_studyuids):
        self.duplicates = list(set(other_studyuids))
        
    
    ###########################################
    ## make case for image types and reader  ##
    ###########################################
    def get_imgos_evals_case(self, task_id):
        db = self.db; self.db = None
        case = copy.deepcopy(self) # mongodb connection not copy-able
        self.db = db; case.db = db
        # get imgos and evals
        case.task_id = task_id
        case.imgos, case.evals = dict(), dict()
        for imagetype in ['SAX CINE', 'SAX CS', 'LAX CINE 2CV', 'LAX CINE 3CV', 'LAX CINE 4CV', 'SAX T1 PRE', 'SAX T1 POST', 'SAX T2', 'SAX LGE', 'SAX ECV']:

            stacknrs = list(set([d['stack_nr'] for d in self.db.imgo_coll.find({'studyuid':self.studyuid, 'imagetype':imagetype},
                                                                               {'_id':0,'stack_nr':1})]))
            if len(stacknrs)!=0: case.imgos[imagetype]=[]
            for stack_i in stacknrs:
                try: imgo = ImageOrganizer(self.db, studyuid=self.studyuid, imagetype=imagetype, stack_nr=stack_i)
                except Exception as e: continue; print(traceback.format_exc()); continue
                try: 
                    if hasattr(imgo, 'depthandtime2sop'): case.imgos[imagetype].append(imgo)
                except Exception as e: continue; print(traceback.format_exc()); continue
            
            stacknrs = list(set([d['stack_nr'] for d in self.db.eval_coll.find({'studyuid':self.studyuid, 'imagetype':imagetype},
                                                                               {'_id':0,'stack_nr':1})]))
            
            if len(stacknrs)!=0: case.evals[imagetype]=[]
            for stack_i in stacknrs:
                try: eva=Evaluation(self.db,studyuid=self.studyuid,task_id=task_id,imagetype=imagetype,stack_nr=stack_i)
                except Exception as e: continue; print(traceback.format_exc()); continue
                try: 
                    if len(eva.available_contours)>0: case.evals[imagetype].append(eva)
                except Exception as e: continue; print(traceback.format_exc()); continue
        return case
                
                
                