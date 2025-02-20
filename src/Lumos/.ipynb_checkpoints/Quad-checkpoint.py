import pymongo
from   pymongo import MongoClient
from   pymongo import IndexModel

import os
import json
import pydicom
from pathlib import Path
import traceback

from Lumos.utils import *


class QUAD_Manager:
    def __init__(self):
        self.client    = MongoClient()
        self.db        = self.client['Lumos_CMR_QualityAssuranceDatabase'] 
        self.dcm_coll  = self.db['dicoms']
        self.anno_coll = self.db['annotations']
        self.imgo_coll = self.db['image_organizers']
        self.eval_coll = self.db['evaluations']
        self.case_coll = self.db['cases']
        self.coho_coll = self.db['cohorts']
        self.pers_coll = self.db['persons'] # rename to actors = NI or AI
        self.task_coll = self.db['task_environments'] # links to readers and 
        
        # DICOMS
        index_dicom_sop = IndexModel([('sop', 1)], unique=True)
        index_study = IndexModel([('studyuid', 1)])
        index_study_imgtype = IndexModel([('studyuid', 1), ('imagetype', 1)])
        self.db['dicoms'].create_indexes([index_dicom_sop, index_study, index_study_imgtype])
        
        # ANNOTATIONS
        index_annos_sop = IndexModel([('task_id', 1), ('sop', 1)], unique=True)
        index_annos_study = IndexModel([('task_id', 1), ('studyuid', 1)])
        self.db['annotations'].create_indexes([index_annos_sop, index_annos_study])
        
        # IMAGE ORGANIZERS
        # what makes image organizers fast to access?
        self.db['image_organizers'].create_index([('studyuid', 1)])
        self.db['image_organizers'].create_index([('studyuid', 1), ('imagetype', 1)])
        self.db['image_organizers'].create_index([('studyuid', 1), ('imagetype', 1), ('stack_nr', 1)], unique=True)
        
        # EVALUATIONS
        self.db['evaluations'].create_index([('task_id', 1)])
        self.db['evaluations'].create_index([('task_id', 1), ('studyuid', 1)])
        self.db['evaluations'].create_index([('task_id', 1), ('studyuid', 1), ('imagetype', 1)])
        self.db['evaluations'].create_index([('task_id', 1), ('studyuid', 1), ('imagetype', 1), ('stack_nr', 1)], unique=True)
        
        # CASES
        # access via reader and studyuid (not unique - e.g. several with different postprocessing software)
        self.db['cases'].create_index([('studyuid', 1)], unique=True)
        
        # COHORTS
        self.db['cohorts'].create_index([('owner', 1)])
        self.db['cohorts'].create_index([('owner', 1), ('name', 1)], unique=True)
        
        # PERSONS
        self.db['persons'].create_index([('firstname', 1), ('lastname', 1), ('birthdate', 1)], unique=True)
        
        # TASK ENVIRONMENTS
        # require no unique ids
        
        
        
    def _drop_collections(self):
        for coll_name in self.db.list_collection_names():
            self.db[coll_name].drop_indexes()
            self.db[coll_name].drop()
    
    
    def insert_dicom(self, dcm):
        try: 
            dcm_json  = json.loads(dcm.to_json())
            fmeta = json.loads(dcm.file_meta.to_json())
            dcm_json['file_meta']  = fmeta
            dcm_json['sop']        = dcm.SOPInstanceUID
            dcm_json['seriesuid']  = dcm.SeriesInstanceUID
            dcm_json['seriesdescription'] = dcm.SeriesDescription
            dcm_json['studyuid']   = dcm.StudyInstanceUID
            try:    dcm_json['imagetype'] = dcm[0x0b, 0x10].value.replace('Lazy Luna: ', '') # try ll tag import =)
            except: dcm_json['imagetype'] = 'Unknown'
            self.dcm_coll.insert_one(dcm_json)
        except Exception as e: print(traceback.format_exc())
        
    def insert_anno(self, json_anno, task_id, studyuid, sop):
        try:
            json_anno['task_id']   = task_id
            json_anno['studyuid']  = studyuid
            json_anno['sop']       = sop
            self.anno_coll.insert_one(json_anno)
        except Exception as e: return; print(traceback.format_exc())
            
    def insert_img_o(self, img_o):
        try:
            imgo_dict = img_o.__dict__
            imgo_dict.pop('db'); imgo_dict.pop('depthandtime2sop')
            self.imgo_coll.insert_one(imgo_dict)
        except Exception as e: return; print(traceback.format_exc())
        
    def insert_eval(self, eva):
        try:
            eva_dict = eva.__dict__
            eva_dict.pop('db')
            eva_dict.pop('imgo')
            eva_dict.pop('depthandtime2sop')
            self.eval_coll.insert_one(eva_dict)
            print('EVA DICT: ', eva_dict)
        except Exception as e: print(traceback.format_exc()); return; 
        
    def insert_case(self, case):
        try:
            case_dict = case.__dict__
            try:    case_dict.pop('db')
            except: print(traceback.format_exc()); pass
            self.case_coll.insert_one(case_dict)
        except Exception as e: print(traceback.format_exc()); return; print(traceback.format_exc())
                
    def insert_cohort(self, cohort): # currently just a dictionary
        self.coho_coll.insert_one(cohort)

    def insert_dicom_folder(quad, folder_path):
        studyuids = set()
        for i_p, p in enumerate(Path(folder_path).glob('**/*.dcm')):
            try:
                dcm = pydicom.dcmread(str(p), stop_before_pixels=False)
                dcmjson = dcm_to_json(dcm, str(p))
                studyuids.add(dcmjson['studyuid'])
                if len(studyuids)>1: break
                quad.dcm_coll.insert_one(dcmjson)
            except: print(traceback.format_exc()); continue
    
    def insert_anno_folder(self, folder_path, task_id, studyuid):
        for i_p, p in enumerate(Path(folder_path).glob('**/*.json')):
            try:
                sop = os.path.basename(p).replace('.json','')
                self.insert_anno(json.load(open(p)), task_id, studyuid, sop)
            except: print(traceback.format_exc()); continue
                
    def insert_person(self, person_dict):
        try: self.pers_coll.insert_one(person_dict)
        except: print(traceback.format_exc())
                
    def insert_task_environment(self, task_dict):
        try: self.task_coll.insert_one(task_dict)
        except: print(traceback.format_exc())