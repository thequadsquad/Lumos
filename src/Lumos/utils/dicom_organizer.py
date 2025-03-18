import os
from pathlib import Path
import pydicom

from functools import reduce
from operator import getitem

import numpy as np

from Lumos.Annotation import *
from Lumos.ImageOrganizer import *


def get_values_from_nested_dict(d):
    for v in d.values():
        if isinstance(v, dict): yield from get_values_from_nested_dict(v)
        else:                   yield v

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, str): result.extend(flatten(el))
        else: result.append(el)
    return result


class Dicom_Organizer:
    def __init__(self, quad, studyuid, task_id=None, by_series_description=True, by_series=False, load=True):
        self.quad               = quad
        self.studyuid           = studyuid
        self.task_id            = task_id
        self.by_seriesdescr     = by_series_description
        self.by_series          = by_series
        if load: self.load_images_and_annos()
    
    def load_images_and_annos(self):
        # GET ANNOS
        self.annos = dict()
        if self.task_id is not None:
            anno_jsons = self.quad.anno_coll.find({'task_id':self.task_id, 'studyuid':self.studyuid})
            self.annos = {a['sop']: Annotation(self.quad, task_id=self.task_id, sop=a['sop']) for a in anno_jsons}
        # GET DCMS
        self.dcms = dict()
        self.has_annotations = dict()
        images = self.quad.dcm_coll.find({'studyuid':self.studyuid}, {'_id':1, 'imagetype':1, 'seriesdescription':1, 
                                                                      'seriesuid':1, 'sop':1})
        for i, img in enumerate(images):
            try:    imagetype = img['imagetype']
            except: imagetype = 'None'
            seriesdescr = img['seriesdescription']
            series_uid  = img['seriesuid']
            sop         = img['sop']
            # INITIATE KEYS IN DICT IN MISSING
            try:
                if imagetype not in self.dcms.keys(): 
                    self.dcms[imagetype] = dict()
                    self.has_annotations[imagetype] = dict()
                if seriesdescr not in self.dcms[imagetype].keys(): 
                    self.dcms[imagetype][seriesdescr] = dict()
                    self.has_annotations[imagetype][seriesdescr] = dict()
                if series_uid not in self.dcms[imagetype][seriesdescr].keys(): 
                    self.dcms[imagetype][seriesdescr][series_uid] = []
                    self.has_annotations[imagetype][seriesdescr][series_uid] = False
                # ADD PATH TO DICT
                if sop in self.annos.keys():
                    self.has_annotations[imagetype][seriesdescr][series_uid] = True
                self.dcms[imagetype][seriesdescr][series_uid].append(sop)
            except Exception as e: print(img, '\nException: ', e)
        self.original_lltag2pathset = self.get_lltag_to_path_set()

    
    def get_section_keys(self, sort_by_has_anno=True):
        if not self.by_seriesdescr and not self.by_series: 
            keys = [(lltag,) for lltag in self.dcms.keys()]
            return sorted(keys, key=lambda k: self.section_has_annotations(k), reverse=True)
        if self.by_seriesdescr and not self.by_series:
            keys = []
            for lltag in self.dcms.keys():
                for seriesdescr in self.dcms[lltag].keys():
                    keys.append((lltag, seriesdescr))
            return sorted(keys, key=lambda k: self.section_has_annotations(k), reverse=True)
        keys = []
        for lltag in self.dcms.keys():
            for seriesdescr in self.dcms[lltag].keys():
                for seriesuid in self.dcms[lltag][seriesdescr].keys():
                    keys.append((lltag, seriesdescr, seriesuid))
        return sorted(keys, key=lambda k: self.section_has_annotations(k), reverse=True)
    
    def get_section(self, key): 
        return reduce(getitem, key, self.dcms)
        
    def get_paths_from_section(self, key):
        section = self.get_section(key)
        if isinstance(section, list): lists = section
        else: lists = [x for x in get_values_from_nested_dict(section)]
        return flatten(lists)
    
    def get_nr_of_paths_from_section(self, key):
        section = self.get_section(key)
        if isinstance(section, list): return len(section)
        lengths = [len(x) for x in get_values_from_nested_dict(section)]
        return sum(lengths)
    
    def get_first_path_from_section(self, key):
        section = self.get_section(key)
        if isinstance(section, list): return section[0]
        return next(get_values_from_nested_dict(section))[0]
    
    def get_first_path_all_sections(self):
        keys = self.get_section_keys()
        return [self.get_first_path_from_section(k) for k in keys]
    
    def get_firstpath_hasanno_nr(self, key):
        firstpath = self.get_first_path_from_section(key)
        has_anno  = self.section_has_annotations(key)
        nr = self.get_nr_of_paths_from_section(key)
        return firstpath, has_anno, nr
    
    def get_key_firstpath_hasanno_nr_all_sections(self):
        keys = self.get_section_keys()
        ret = []
        for k in keys:
            #print(k)
            fpath, has_anno, nr = self.get_firstpath_hasanno_nr(k)
            ret.append((k, fpath, has_anno, nr))
        return ret
    
    def set_lltag_for_dcms(self, dcm_paths, old_lltags, new_lltags):
        old_sections, new_sections = [], []
        for p, ol, nl in zip(dcm_paths, old_lltags, new_lltags):
            if ol==nl: continue
            dcm_info = self.quad.dcm_coll.find_one({'sop': p}, {'seriesdescription':1, 'seriesuid':1})
            seriesdescr = dcm_info['seriesdescription']
            series_uid  = dcm_info['seriesuid']
            # remove from old key's list
            old_key = (ol, seriesdescr, series_uid)
            self.dcms[ol][seriesdescr][series_uid].remove(p)
            # add to new key's list
            new_key = (nl, seriesdescr, series_uid)
            self.make_section_ifnotexists(new_key)
            self.dcms[nl][seriesdescr][series_uid].append(p)
            old_sections.append(old_key)
            new_sections.append(new_key)
        for key in set(old_sections):
            if len(self.get_section(key))==0: self.delete_section(key); continue
            ol, seriesdescr, series_uid = key
            self.has_annotations[ol][seriesdescr][series_uid] = self.section_has_annotations(key)
        for key in set(new_sections):
            nl, seriesdescr, series_uid = key
            self.has_annotations[nl][seriesdescr][series_uid] = self.section_has_annotations(key)
    
    def set_lltag_for_section(self, origin_key, lltag):
        if origin_key[0]==lltag: return # no change
        new_key = list(origin_key); new_key[0] = lltag; new_key = tuple(new_key)
        # make destination if not exists
        self.make_destination_from_origin_ifnotexists(new_key, origin_key)
        # INSERT into destination (append all lists on lowest level) 
        self.insert_section(new_key, origin_key)
        # Delete former section
        self.delete_section(origin_key)
    
    def insert_section(self, destination_key, origin_key):
        paths = self.get_paths_from_section(origin_key)
        lltag = destination_key[0]
        for i_p, p in enumerate(paths):
            dcm_info = self.quad.dcm_coll.find_one({'sop': p}, {'seriesdescription':1, 'seriesuid':1})
            seriesdescr = dcm_info['seriesdescription']
            series_uid  = dcm_info['seriesuid']
            self.dcms[lltag][seriesdescr][series_uid].append(p)
            self.has_annotations[lltag][seriesdescr][series_uid] = True # is this sensible??? shouldn't it be recalculated?
        
    def make_destination_from_origin_ifnotexists(self, destination_key, origin_key):
        assert len(destination_key)==len(origin_key), print("Failed in Make Destination")
        dkey = destination_key
        okey = origin_key
        try:
            if dkey[0] not in self.dcms.keys():
                self.dcms[dkey[0]] = dict(); self.has_annotations[dkey[0]] = dict()
        except: pass
        try:
            if dkey[1] not in self.dcms[dkey[0]].keys():
                self.dcms[dkey[0]][dkey[1]] = dict(); self.has_annotations[dkey[0]][dkey[1]] = dict()
        except: pass
        try:
            if dkey[2] not in self.dcms[dkey[0]][dkey[1]].keys():
                self.dcms[dkey[0]][dkey[1]][dkey[2]]=[]
                self.has_annotations[dkey[0]][dkey[1]][dkey[2]] = False
        except: pass
        if len(origin_key)<3: # make the sub levels as well
            section = self.get_section(origin_key)
            for k in section.keys():
                ok = origin_key+(k,)
                dk = destination_key+(k,)
                self.make_destination_from_origin_ifnotexists(dk, ok)
    
    def delete_section(self, k):
        if len(k)==3: 
            del self.dcms[k[0]][k[1]][k[2]]; del self.has_annotations[k[0]][k[1]][k[2]]
            if len(self.dcms[k[0]][k[1]])==0: self.delete_section((k[0],k[1]))
        if len(k)==2: 
            del self.dcms[k[0]][k[1]]; del self.has_annotations[k[0]][k[1]]
            if len(self.dcms[k[0]])==0: self.delete_section((k[0],))
        if len(k)==1: 
            del self.dcms[k[0]]; del self.has_annotations[k[0]]
    
    def section_has_annotations(self, key):
        anno_section = reduce(getitem, key, self.has_annotations)
        if isinstance(anno_section, bool): return anno_section
        bools = [int(x) for x in get_values_from_nested_dict(anno_section)]
        return sum(bools)>0
    
    def get_lltag_to_path_set(self):
        lltag2paths = dict()
        for lltag in self.dcms.keys(): lltag2paths[lltag] = set()
        for key in self.get_section_keys():
            paths = self.get_paths_from_section(key)
            lltag2paths[key[0]] = lltag2paths[key[0]].union(set(paths))
        return lltag2paths
        
    def store_dicoms_with_tags(self):
        new_lltag2pathset = self.get_lltag_to_path_set()
        all_keys = set(new_lltag2pathset.keys()).union(self.original_lltag2pathset.keys())
        for k in all_keys:
            if k not in new_lltag2pathset:           new_lltag2pathset[k]           = set()
            if k not in self.original_lltag2pathset: self.original_lltag2pathset[k] = set()
        for lltag in all_keys:
            paths = new_lltag2pathset[lltag].difference(self.original_lltag2pathset[lltag])
            for p in paths:
                self.quad.dcm_coll.update_one({'sop': p}, {'$set': {'imagetype': lltag.replace('New: ','')}}, upsert=False)

        
    def make_section_ifnotexists(self, key):
        if len(key)>0 and key[0] not in self.dcms.keys():                 self.dcms[key[0]] = dict()
        if len(key)>1 and key[1] not in self.dcms[key[0]].keys():         self.dcms[key[0]][key[1]] = dict()
        if len(key)>2 and key[2] not in self.dcms[key[0]][key[1]].keys(): self.dcms[key[0]][key[1]][key[2]] = []
        if len(key)>0 and key[0] not in self.has_annotations.keys():      
            self.has_annotations[key[0]] = dict()
        if len(key)>1 and key[1] not in self.has_annotations[key[0]].keys():
            self.has_annotations[key[0]][key[1]] = dict()
        if len(key)>2 and key[2] not in self.has_annotations[key[0]][key[1]].keys():
            self.has_annotations[key[0]][key[1]][key[2]] = False
        
    def __str__(self):
        string = 'DCMS Dictionary\n'
        for lltag in self.dcms.keys():
            string += lltag+'\n'
            for seriesdescr in self.dcms[lltag].keys():
                string += '\t' + seriesdescr + '\n'
                for seriesuid in self.dcms[lltag][seriesdescr].keys():
                    string += '\t\t' + seriesuid + ' nr imgs: ' + str(len(self.dcms[lltag][seriesdescr][seriesuid])) 
                    string += ' has anno: '+str(self.has_annotations[lltag][seriesdescr][seriesuid])+'\n'
        return string

