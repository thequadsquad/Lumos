import Lumos
from Lumos.Views import *
from Lumos.ImageOrganizer import *

import math
import numpy as np

## Evaluation/Report
class Evaluation:
    # Two scenarios of initializing an Evaluation
    # 1) DB contains the Evaluation
    #    Load the evaluation and the imgo that belongs to it, instantiate all fields, done
    # 2) DB contains only ImgOrganizer and Annotations
    #    Cannot load the eval object... try loading the ImgO object and set the raeder name
    #    call "calculate_clinical_parameters" in order to compute the evaluation object
    def __init__(self, db=None, task_id=None, studyuid=None, imagetype=None, stack_nr=0):
        assert type(db)==Lumos.Quad.QUAD_Manager, 'quad should be of type Lumos.Quad.QUAD_Manager'
        if None not in [task_id, imagetype, studyuid, stack_nr]: 
            try: self.__dict__ = db.eval_coll.find_one({'task_id':task_id, 'studyuid':studyuid, 'imagetype':imagetype, 'stack_nr':stack_nr})
            except Exception as e: pass
        self.db = db
        
        # raise exception if not exists?
        # take and and create from img_organizer?
        if None not in [imagetype, studyuid]:
            try:
                self.imgo = ImageOrganizer(db, studyuid=studyuid, imagetype=imagetype, stack_nr=stack_nr)
            except Exception as e: pass#; print(traceback.format_exc())
            try:
                #print('Here: ', self.imgo.__dict__.keys())
                self.name, self.age, self.sex = self.imgo.name, self.imgo.age, self.imgo.sex
                self.weight, self.size = self.imgo.weight, self.imgo.size
                self.nr_slices, self.nr_phases = self.imgo.nr_slices, self.imgo.nr_phases
                self.depthandtime2sop = self.imgo.depthandtime2sop
                self.task_id    = task_id
                task = db.task_coll.find_one({'_id': task_id})
                self.taskname = task['displayname']
                self.studyuid  = studyuid
                self.imagetype = imagetype
                self.stack_nr   = stack_nr
                self.missing_slices = self.imgo.missing_slices
                self.spacing_between_slices = self.imgo.spacing_between_slices
                self.slice_thickness = self.imgo.slice_thickness
                self.pixel_h, self.pixel_w = self.imgo.pixel_h, self.imgo.pixel_w
            except Exception as e: pass; #print(traceback.format_exc())
        
    def get_dcm(self, slice_nr, phase_nr):
        return self.imgo.get_dcm(slice_nr, phase_nr)
        
    def get_img(self, slice_nr, phase_nr):
        return self.imgo.get_img(slice_nr, phase_nr)
    
    def get_anno(self, slice_nr, phase_nr):
        return Annotation(db=self.db, task_id=self.task_id, sop=self.depthandtime2sop[(slice_nr, phase_nr)])
    
    def get_img_anno(self, slice_nr, phase_nr):
        return self.get_img(slice_nr, phase_nr), self.get_anno(slice_nr, phase_nr)
    
    def get_threshold(self, slice_nr, phase_nr, string=False):
        anno   = self.get_anno(slice_nr, phase_nr)
        thresh = anno.get_threshold('thresh') 
        return "{:.2f}".format(thresh) if string else thresh
    
    def evaluate(self):
        self.available_contours = self.get_available_contours() # get all contour types added for this reader
                
        self.bounding_box = self.get_bounding_box() # get boundingbox and  areas by slice and phase
            
        if 'SAX CINE'     in self.imagetype: v = SAX_CINE_View()
        if 'LAX CINE 2CV' in self.imagetype: v = LAX_CINE_2CV_View()
        if 'LAX CINE 4CV' in self.imagetype: v = LAX_CINE_4CV_View()
        if 'SAX T1 PRE'   in self.imagetype: v = SAX_T1_PRE_View()
        if 'SAX T2'       in self.imagetype: v = SAX_T2_View()
        if 'SAX T1 POST'  in self.imagetype: v = SAX_T1_POST_View()
        if 'SAX LGE'      in self.imagetype: v = SAX_LGE_View()
        
        # get clinical results
        self.clinical_parameters = dict()
        for cr_name, cr in v.clinical_parameters.items(): 
            val = float(cr.get_val(self))
            if not math.isnan(val): self.clinical_parameters[cr_name] = [val, cr.unit]
        
        # aha model if mapping
        if 'T1' in self.imagetype or 'T2' in self.imagetype:
            try:
                aha_names, aha_means, aha_stds = self.calculate_aha_segments()
                self.aha_model = {aha_names[i][j]:(aha_means[i][j], aha_stds[i][j]) for i in range(3) for j in range(len(aha_names[i]))}
            except Exception as e: print(traceback.format_exc())
    
    def get_volume(self, phase, cont_name):
        if np.isnan(phase): raise Exception('Volume calculation not possible: phase=np.nan.') 
        annos = [self.get_anno(d, phase) for d in range(self.nr_slices)]
        pixel_area = self.pixel_h * self.pixel_w
        areas = [a.get_contour(cont_name).area*pixel_area if a is not None else 0.0 for a in annos]
        has_conts = [a!=0 for a in areas]
        if True not in has_conts: return 0
        base_idx = has_conts.index(True)
        apex_idx = self.nr_slices - has_conts[::-1].index(True) - 1
        vol = 0
        for d in range(self.nr_slices):
            pixel_depth = (self.slice_thickness+self.spacing_between_slices)/2.0 if d in [base_idx, apex_idx] else self.spacing_between_slices
            vol += areas[d] * pixel_depth
        # for missing slices
        for d in self.missing_slices:
            pixel_depth = self.spacing_between_slices
            vol += (areas[d] + areas[d+1])/2 * pixel_depth
        return vol / 1000.0
    
    def get_available_contours(self):
        available_contours = set()
        for d in range(self.nr_slices):
            for p in range(self.nr_phases):
                try:    anno = self.get_anno(d,p)
                except: continue
                for cname in anno.available_contour_names(): available_contours.add(cname)
        return list(available_contours)
    
    def get_bounding_box(self):
        bounds = []
        for d in range(self.nr_slices):
            for p in range(self.nr_phases):
                anno = self.get_anno(d,p)
                for cname in anno.available_contour_names(): 
                    bounds.append(anno.get_contour(cname).bounds)
        bounds = np.asarray(bounds)
        xmin, ymin, _, _ = np.min(bounds, axis=0); _, _, xmax, ymax = np.max(bounds, axis=0)
        h, w = self.imgo.height, self.imgo.width
        bounding_box = (max(xmin,0), min(xmax,w), max(ymin,0), min(ymax,h))
        return bounding_box
    
    def calculate_aha_segments(self):
        # returns means and stds
        if self.nr_slices == 1: # assume midventricular
            img, anno = self.get_img_anno(0,0)
            m = anno.get_myo_mask_by_angles(img, nr_bins=6)
            m_m = np.asarray([np.mean(v) for v in m.values()])
            m_s = np.asarray([np.std(v) for v in m.values()])
            return ([['Basal Anterior', 'Basal Antero-Septal', 'Basal Infero-Septal', 'Basal Inferior', 'Basal Infero-Lateral', 'Basal Antero-Lateral'],
                     ['Mid Anterior', 'Mid Antero-Septal', 'Mid Infero-Septal', 'Mid Inferior', 'Mid Infero-Lateral', 'Mid Antero-Lateral'],
                     ['Apical Lateral', 'Apical Septal', 'Apical Inferior', 'Apical Anterior']],
                    [np.full(6,np.nan), np.roll(m_m,1), np.full(4,np.nan)],
                    [np.full(6,np.nan), np.roll(m_s,1), np.full(4,np.nan)])
        
        if self.nr_slices == 3: # assume 3 of 5 so: 0:base, 1:midv, 2:apex
            try:
                img,  anno = self.get_img_anno(0,0)
                b   = anno.get_myo_mask_by_angles(img, nr_bins=6)
                b_m = np.asarray([np.mean(v) for v in b.values()])
                b_s = np.asarray([np.std(v) for v in b.values()])
            except:
                b_m = np.empty((6,)); b_m.fill(np.nan)
                b_s = np.empty((6,)); b_s.fill(np.nan)
            try:
                img,  anno = self.get_img_anno(1,0)
                m   = anno.get_myo_mask_by_angles(img, nr_bins=6)
                m_m = np.asarray([np.mean(v) for v in m.values()])
                m_s = np.asarray([np.std(v) for v in m.values()])
            except:
                m_m = np.empty((6,)); m_m.fill(np.nan)
                m_s = np.empty((6,)); m_s.fill(np.nan)
            try:
                img,  anno = self.get_img_anno(2,0)
                a   = anno.get_myo_mask_by_angles(img, nr_bins=4)
                a_m = np.asarray([np.mean(v) for v in a.values()])
                a_s = np.asarray([np.std(v) for v in a.values()])
            except:
                a_m = np.empty((4,)); a_m.fill(np.nan)
                a_s = np.empty((4,)); a_s.fill(np.nan)
            means = [a.tolist() for a in [np.roll(b_m,1),np.roll(m_m,1),np.roll(a_m,1)]]
            stds  = [a.tolist() for a in [np.roll(b_s,1),np.roll(m_s,1),np.roll(a_s,1)]]
            names = [['Basal Anterior', 'Basal Antero-Septal', 'Basal Infero-Septal', 'Basal Inferior', 'Basal Infero-Lateral', 'Basal Antero-Lateral'],
                     ['Mid Anterior', 'Mid Antero-Septal', 'Mid Infero-Septal', 'Mid Inferior', 'Mid Infero-Lateral', 'Mid Antero-Lateral'],
                     ['Apical Lateral', 'Apical Septal', 'Apical Inferior', 'Apical Anterior']]
            return names, means, stds
        
        
    def get_patient_info(self):
        dcm = utils.unpack_dcm(self.db.dcm_coll.find_one({'studyuid' : self.studyuid}))
        info = map(str, [dcm.PatientName, dcm.PatientAge, dcm.PatientSex, dcm.PatientWeight, dcm.PatientSize])
        return info