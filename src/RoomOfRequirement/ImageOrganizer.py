from operator import itemgetter
import numpy as np
import pydicom
from time import time
import traceback
import RoomOfRequirement

class ImageOrganizer:
    def __init__(self, db, studyuid=None, imagetype=None):
        assert type(db)==RoomOfRequirement.Quad.QUAD_Manager, 'quad should be of type RoomOfRequirement.Quad.QUAD_Manager'
        self.studyuid  = studyuid
        self.imagetype = imagetype
        imgo = db.imgo_coll.find_one({'studyuid': studyuid, 'imagetype': imagetype})
        if imgo is not None: 
            self.__dict__ = imgo
            self.depthandtime2sop = {tuple(v):k for k,v in self.sop2depthandtime.items()}
            self.__dict__.pop('_id')
        self.db = db # DB must be passed bc it cannot be stored, must be set After the dict instantiation
    
    def organize(self, sops=None):
        # get the dicoms
        db = self.db
        if sops is not None:                            img_jsons = list(db.dcm_coll.find({'sop': {'$in': sops}}))
        if None not in [self.studyuid, self.imagetype]: img_jsons = list(db.dcm_coll.find({'studyuid': self.studyuid, 'imagetype': self.imagetype}))
        try:    self.imagetype = img_jsons[0]['imagetype']
        except: self.imagetype = 'Unknown'
        
        dicoms = [pydicom.dcmread(j['path']) for j in img_jsons]
        dcm = dicoms[0]
        self.studyuid          = dcm.StudyInstanceUID
        self.sop2depthandtime  = self.get_sop2depthandtime(dicoms)
        self.depthandtime2sop  = {v:k for k,v in self.sop2depthandtime.items()}
        self.set_nr_slices_phases()
        self.set_image_height_width_depth({dcm.SOPInstanceUID: dcm for dcm in dicoms})
        
        self.name, self.age, self.sex, self.weight, self.size = self.get_patient_info()
        # more important fields
        try:   self.field_strength     = dcm.MagneticFieldStrength
        except Exception as e: print(e); pass
        try:   self.software_versions  = dcm.SoftwareVersions
        except Exception as e: print(e); pass
        try:   self.flip_angle         = dcm.FlipAngle
        except Exception as e: print(e); pass
        try:   self.pixel_spacing      = [float(p) for p in dcm.PixelSpacing]
        except Exception as e: print(e); pass
        try:   self.manufacture_model  = dcm.ManufacturerModelName
        except Exception as e: print(e); pass
        try:   self.site               = dcm.InstitutionalDepartmentName
        except Exception as e: print(e); pass
        
    # try a sort function as in dcmlabeling_1_tab
    def get_sop2depthandtime(self, dicoms):
        # returns dict sop --> (depth, time)
        imgs = {dcm.SOPInstanceUID: dcm for dcm in dicoms}
        sortable = [[k,v.SliceLocation,v.InstanceNumber] for k,v in imgs.items()]
        slice_nrs = {x:i for i,x in enumerate(sorted(list(set([x[1] for x in sortable]))))}
        sortable = [s+[slice_nrs[s[1]]] for s in sortable]
        sortable_by_slice = {d:[] for d in slice_nrs.values()}
        for s in sortable: sortable_by_slice[s[-1]].append(s)
        for d in range(len(sortable_by_slice.keys())):
            sortable_by_slice[d] = sorted(sortable_by_slice[d], key=lambda s:s[2])
            for p in range(len(sortable_by_slice[d])):
                sortable_by_slice[d][p].append(p)
        sop2depthandtime = dict()
        for d in range(len(sortable_by_slice.keys())):
            for s in sortable_by_slice[d]:
                sop2depthandtime[s[0]] = (s[-2],s[-1])
        # flip slice direction if : base top x0<x1, y0>y1, z0>z1, apex top x0>x1, y0<y1, z0<z1
        depthandtime2sop = {v:k for k,v in sop2depthandtime.items()}
        try: img1, img2 = imgs[depthandtime2sop[(0,0)]], imgs[depthandtime2sop[(1,0)]]
        except: return sop2depthandtime
        img1x,img1y,img1z = list(map(float,img1.ImagePositionPatient))
        img2x,img2y,img2z = list(map(float,img2.ImagePositionPatient))
        if img1x<img2x and img1y>img2y and img1z>img2z: pass
        else: #img1x>img2x or img1y<img2y or img1z<img2z:
            max_depth = max(sortable_by_slice.keys())
            for sop in sop2depthandtime.keys():
                sop2depthandtime[sop] = (max_depth-sop2depthandtime[sop][0], sop2depthandtime[sop][1])
        return sop2depthandtime
    
    def set_image_height_width_depth(self, dicom_dict):
        nr_slices = self.nr_slices
        dcm1 = dicom_dict[self.depthandtime2sop[(0, 0)]]
        self.height, self.width = dcm1.pixel_array.shape
        self.pixel_h, self.pixel_w = list(map(float, dcm1.PixelSpacing))
        try: dcm2 = dicom_dict[self.depthandtime2sop[(1, 0)]]
        except Exception as e: 
            #print(e)
            self.slice_thickness = dcm1.SliceThickness
            self.spacing_between_slices = dcm1.SliceThickness
            self.missing_slices = []
            return
        spacingbs = [] #spacings between slices
        for d in range(nr_slices-1):
            dcm1 = dicom_dict[self.depthandtime2sop[(d,   0)]]
            dcm2 = dicom_dict[self.depthandtime2sop[(d+1, 0)]]
            spacingbs += [round(np.abs(dcm1.SliceLocation - dcm2.SliceLocation), 2)]
            try: self.slice_thickness = dcm1.SliceThickness
            except Exception as e: print(e)
        try:
            self.spacing_between_slices = min(spacingbs)
            self.missing_slices = []
            for d in range(nr_slices-1):
                dcm1 = dicom_dict[self.depthandtime2sop[(d,   0)]]
                dcm2 = dicom_dict[self.depthandtime2sop[(d+1, 0)]]
                curr_spacing = round(np.abs(dcm1.SliceLocation - dcm2.SliceLocation), 2)
                if round(curr_spacing / self.spacing_between_slices) != 1:
                    for m in range(int(round(curr_spacing / self.spacing_between_slices))-1):
                        self.missing_slices += [(d + m)]
        except Exception as e: print(e)

    def set_nr_slices_phases(self):
        dat = list(self.depthandtime2sop.keys())
        self.nr_phases = max(dat, key=itemgetter(1))[1]+1
        self.nr_slices = max(dat, key=itemgetter(0))[0]+1
        
    def get_json(self, slice_nr, phase_nr):
        sop  = self.depthandtime2sop[(slice_nr, phase_nr)]
        json = self.db.dcm_coll.find_one({'sop': sop})
        return json
        
    def get_dcm(self, slice_nr, phase_nr):
        dcm = pydicom.dcmread(self.get_json(slice_nr, phase_nr)['path'])
        return dcm

    def get_img(self, slice_nr, phase_nr, normalize=True):
        #try:
        dcm = self.get_dcm(slice_nr, phase_nr)
        img = self.image_normalize(dcm) if normalize else dcm.pixel_array
        #except Exception as e:
        #    print(e)
        #    img = np.zeros((self.height, self.width))
        return img
    
    def image_normalize(self, dcm, value_normalize=None, window_normalize=None):
        img = dcm.pixel_array
        if value_normalize is None or window_normalize is None:
            if 'CINE' in self.imagetype or 'CS' in self.imagetype: value_normalize, window_normalize = True, True
            if 'T1'   in self.imagetype: value_normalize, window_normalize = True, False
            if 'T2'   in self.imagetype: value_normalize, window_normalize = True, False
            if 'LGE'  in self.imagetype: value_normalize, window_normalize = True, False
        if value_normalize:
            if [0x0028, 0x1052] in dcm and [0x0028, 0x1053] in dcm:
                img = img * float(dcm[0x0028, 0x1053].value) + float(dcm[0x0028, 0x1052].value)
        if window_normalize:
            minn, maxx = 0, 255
            if [0x0028, 0x1050] in dcm and [0x0028, 0x1051] in dcm:
                c = float(dcm[0x0028, 0x1050].value) # window center
                w = float(dcm[0x0028, 0x1051].value) # window width
                search_if, search_elif   = img<=(c-0.5)-((w-1)/2), img>(c-0.5)+((w-1)/2)
                img = ((img-(c-0.5)) / (w-1)+0.5) * (maxx-minn) + minn
                img[search_if]   = minn
                img[search_elif] = maxx
        return img
    
    def get_imgs_phase(self, phase_nr, value_normalize=True, window_normalize=True):
        return [self.get_img(d, phase_nr, value_normalize, window_normalize) for d in range(self.nr_slices)]
    
    def get_patient_info(self):
        dcm  = pydicom.dcmread(self.db.dcm_coll.find_one({'studyuid' : self.studyuid})['path'])
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
