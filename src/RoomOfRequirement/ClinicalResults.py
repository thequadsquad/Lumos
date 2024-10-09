####################
# Clinical Results #
####################

import traceback
import numpy as np


# decorator function for exception handling
def CR_exception_handler(f):
    def inner_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            #print(f.__name__ + ' failed to calculate the clinical result. Returning np.nan. Error traceback:')
            #print(traceback.format_exc())
            return np.nan
    return inner_function


class Clinical_Result:
    """Clinical_Result is a class for the calculation, comparison and presentation of clinical parameters
    
        Arguments:
            case (LazyLuna.Containers.Case): a case for which the parameter is calculated
            
        Attributes:
            case (LazyLuna.Containers.Case): a case for which the parameter is calculated
            unit (str): unit name for display
            tol_range (float): acceptable deviation of clinical result 
    """
    def __init(self):
        self.name = ''
        self.unit = '[]'
        self.tol_range = 0
        
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        """Calculates the clinical parameter for its case
            
        Args:
            string (bool): If True provides the first two decimal points as a string
            
        Returns:
            (float | str): the clinical parameter
        """
        pass
    
    def get_val_diff(self, eval1, eval2, string=False):
        """Calculates the clinical parameter difference between this and other case
            
        Args:
            other (LazyLuna.Containers.Case): The case to which the clinical parater is compared
            string (bool): If True provides the first two decimal points as a string
            
        Returns:
            (float | str): the clinical parameter difference
        """
        pass

    

# Phases
class LVSAX_ESPHASE(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'LVESP'
        self.unit = '[#]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        if 'lv_endo' not in evaluation.available_contours: raise Exception('No lv_endo contours for phase calucation.')
        lvendo_vol_curve = [evaluation.get_volume(p, 'lv_endo') for p in range(evaluation.nr_phases)]
        lvpamu_vol_curve = [evaluation.get_volume(p, 'lv_pamu') for p in range(evaluation.nr_phases)]
        vol_curve = np.array(lvendo_vol_curve) - np.array(lvpamu_vol_curve)
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        valid_idx = np.where(vol_curve > 0)[0]
        phase = valid_idx[vol_curve[valid_idx].argmin()]
        return str(phase) if string else phase

    def get_val_diff(self, eval1, eval2, string=False):
        p1, p2, nrp = self.get_val(eval1), self.get_val(eval2), eval1.nr_phases
        cr_diff = min(abs(p1-p2), (min(p1,p2) - max(p1,p2)) % nrp) # module ring difference
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LVSAX_EDPHASE(LVSAX_ESPHASE):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'LVEDP'
        self.unit = '[#]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        if 'lv_endo' not in evaluation.available_contours: raise Exception('No lv_endo contours for phase calucation.')
        lvendo_vol_curve = [evaluation.get_volume(p, 'lv_endo') for p in range(evaluation.nr_phases)]
        lvpamu_vol_curve = [evaluation.get_volume(p, 'lv_pamu') for p in range(evaluation.nr_phases)]
        vol_curve = np.array(lvendo_vol_curve) - np.array(lvpamu_vol_curve)
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        phase = vol_curve.argmax()
        return str(phase) if string else phase
    
    def get_val_diff(self, eval1, eval2, string=False):
        p1, p2, nrp = self.get_val(eval1), self.get_val(eval2), eval1.nr_phases
        cr_diff = min(abs(p1-p2), (min(p1,p2) - max(p1,p2)) % nrp) # module ring difference
        return "{:.2f}".format(cr_diff) if string else cr_diff

class RVSAX_ESPHASE(LVSAX_ESPHASE):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'RVESP'
        self.unit = '[#]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        if 'rv_endo' not in evaluation.available_contours: raise Exception('No rv_endo contours for phase calucation.')
        rvendo_vol_curve = [evaluation.get_volume(p, 'rv_endo') for p in range(evaluation.nr_phases)]
        rvpamu_vol_curve = [evaluation.get_volume(p, 'rv_pamu') for p in range(evaluation.nr_phases)]
        vol_curve = np.array(rvendo_vol_curve) - np.array(rvpamu_vol_curve)
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        valid_idx = np.where(vol_curve > 0)[0]
        phase = valid_idx[vol_curve[valid_idx].argmin()]
        return str(phase) if string else phase

    def get_val_diff(self, eval1, eval2, string=False):
        p1, p2, nrp = self.get_val(eval1), self.get_val(eval2), eval1.nr_phases
        cr_diff = min(abs(p1-p2), (min(p1,p2) - max(p1,p2)) % nrp) # module ring difference
        return "{:.2f}".format(cr_diff) if string else cr_diff

class RVSAX_EDPHASE(LVSAX_ESPHASE):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'RVEDP'
        self.unit = '[#]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        if 'rv_endo' not in evaluation.available_contours: raise Exception('No rv_endo contours for phase calucation.')
        rvendo_vol_curve = [evaluation.get_volume(p, 'rv_endo') for p in range(evaluation.nr_phases)]
        rvpamu_vol_curve = [evaluation.get_volume(p, 'rv_pamu') for p in range(evaluation.nr_phases)]
        vol_curve = np.array(rvendo_vol_curve) - np.array(rvpamu_vol_curve)
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        phase = vol_curve.argmax()
        return str(phase) if string else phase

    def get_val_diff(self, eval1, eval2, string=False):
        p1, p2, nrp = self.get_val(eval1), self.get_val(eval2), eval1.nr_phases
        cr_diff = min(abs(p1-p2), (min(p1,p2) - max(p1,p2)) % nrp) # module ring difference
        return "{:.2f}".format(cr_diff) if string else cr_diff

class NR_SLICES(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'NrSlices'
        self.unit = '[#]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        return str(evaluation.nr_slices) if string else evaluation.nr_slices

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1) - self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff


class LVSAX_ESV(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = 7.3

    def set_CR_information(self):
        self.name = 'LVESV'
        self.unit = '[ml]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    phase = evaluation.clinical_parameters[LVSAX_ESPHASE.name][0]
        except: phase = LVSAX_ESPHASE().get_val(evaluation)
        cr = evaluation.get_volume(phase, 'lv_endo') - evaluation.get_volume(phase, 'lv_pamu')
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LVSAX_EDV(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = 10.8

    def set_CR_information(self):
        self.name = 'LVEDV'
        self.unit = '[ml]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    phase = evaluation.clinical_parameters[LVSAX_EDPHASE.name][0]
        except: phase = LVSAX_EDPHASE().get_val(evaluation)
        cr = evaluation.get_volume(phase, 'lv_endo') - evaluation.get_volume(phase, 'lv_pamu')
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class RVSAX_ESV(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = 9.7

    def set_CR_information(self):
        self.name = 'RVESV'
        self.unit = '[ml]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    phase = evaluation.clinical_parameters[RVSAX_ESPHASE.name][0]
        except: phase = RVSAX_ESPHASE().get_val(evaluation)
        cr = evaluation.get_volume(phase, 'rv_endo') - evaluation.get_volume(phase, 'rv_pamu')
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class RVSAX_EDV(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = 14.6

    def set_CR_information(self):
        self.name = 'RVEDV'
        self.unit = '[ml]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    phase = evaluation.clinical_parameters[RVSAX_EDPHASE.name][0]
        except: phase = RVSAX_EDPHASE().get_val(evaluation)
        cr = evaluation.get_volume(phase, 'rv_endo') - evaluation.get_volume(phase, 'rv_pamu')
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

    
class LVSAX_MYO(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = 13.3

    def set_CR_information(self):
        self.name = 'LVM'
        self.unit = '[g]'
        
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    phase = evaluation.clinical_parameters[LVSAX_EDPHASE.name][0]
        except: phase = LVSAX_EDPHASE().get_val(evaluation)
        cr = 1.05 * evaluation.get_volume(phase, 'lv_myo')
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class RVSAX_MYO(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'RVM'
        self.unit = '[g]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    phase = evaluation.clinical_parameters[RVSAX_EDPHASE.name][0]
        except: phase = RVSAX_EDPHASE().get_val(evaluation)
        cr = 1.05 * evaluation.get_volume(phase, 'rv_myo')
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class RVSAX_SV(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = 13.2

    def set_CR_information(self):
        self.name = 'RVSV'
        self.unit = '[ml]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    esv = evaluation.clinical_parameters[RVSAX_ESV.name][0]
        except: esv = RVSAX_ESV().get_val(evaluation)
        try:    edv = evaluation.clinical_parameters[RVSAX_EDV.name][0]
        except: edv = RVSAX_EDV().get_val(evaluation)
        return "{:.2f}".format(edv - esv) if string else edv - esv

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class RVSAX_EF(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = 5.5

    def set_CR_information(self):
        self.name = 'RVEF'
        self.unit = '[%]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    esv = evaluation.clinical_parameters[RVSAX_ESV.name][0]
        except: esv = RVSAX_ESV().get_val(evaluation)
        try:    edv = evaluation.clinical_parameters[RVSAX_EDV.name][0]
        except: edv = RVSAX_EDV().get_val(evaluation)
        cr = 100 * (edv - esv) / (edv + 10e-9) if esv!=0 else np.nan 
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LVSAX_SV(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = 4.5

    def set_CR_information(self):
        self.name = 'LVSV'
        self.unit = '[ml]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    esv = evaluation.clinical_parameters[LVSAX_ESV.name][0]
        except: esv = LVSAX_ESV().get_val(evaluation)
        try:    edv = evaluation.clinical_parameters[LVSAX_EDV.name][0]
        except: edv = LVSAX_EDV().get_val(evaluation)
        return "{:.2f}".format(edv - esv) if string else edv - esv

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LVSAX_EF(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = 5.3

    def set_CR_information(self):
        self.name = 'LVEF'
        self.unit = '[%]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    esv = evaluation.clinical_parameters[LVSAX_ESV.name][0]
        except: esv = LVSAX_ESV().get_val(evaluation)
        try:    edv = evaluation.clinical_parameters[LVSAX_EDV.name][0]
        except: edv = LVSAX_EDV().get_val(evaluation)
        cr = 100 * (edv - esv) / (edv + 10e-9) if esv!=0 else np.nan 
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff


class LVSAX_ESPAPMUM(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = np.nan

    def set_CR_information(self):
        self.name = 'LVESPAPMUM'
        self.unit = '[g]'
        
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    phase = evaluation.clinical_parameters[LVSAX_ESPHASE.name][0]
        except: phase = LVSAX_ESPHASE().get_val(evaluation)
        cr = 1.05 * evaluation.get_volume(phase, 'lv_pamu')
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

    
class LVSAX_EDPAPMUM(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        self.tol_range = np.nan

    def set_CR_information(self):
        self.name = 'LVEDPAPMUM'
        self.unit = '[g]'
        
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    phase = evaluation.clinical_parameters[LVSAX_EDPHASE.name][0]
        except: phase = LVSAX_EDPHASE().get_val(evaluation)
        cr = 1.05 * evaluation.get_volume(phase, 'lv_pamu')
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff
    

###########
# LGE CRs #
###########
########################
# LV Values:           #
# LGE SAX              #
########################

class MYO_MASS(Clinical_Result):
    def __init__(self):
        self.name = 'MYO_MASS'
        self.unit = '[g]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string = False): 
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        #if 'lv_myo' not in evaluation.available_contours: raise Exception('No lv_myo contours for volume calculation.')
        lv_myo_vol = 1.05 * evaluation.get_volume(0, 'lv_myo')   #phase is zero 
        return lv_myo_vol
        
    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class SCAR_MASS(Clinical_Result):
    def __init__(self):
        self.name = 'SCAR_MASS'
        self.unit = '[g]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string = False): 
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        lv_scar_vol = 1.05 * evaluation.get_volume(0, 'lv_scar')  
        return lv_scar_vol

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff


class SCAR_PCT(Clinical_Result):
    def __init__(self): 
        self.name = 'SCAR_PCT'
        self.unit = '[%]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string = False): 
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        lv_scar_vol = evaluation.get_volume(0, 'lv_scar')  
        lv_myo_vol  = evaluation.get_volume(0, 'lv_myo')   
        lv_scar_pct = (lv_scar_vol / lv_myo_vol) *100
        return lv_scar_pct
        
    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff
            

class EX_VOL(Clinical_Result):
    def __init__(self):
        self.name = 'EXCL_VOL'
        self.unit = '[ml]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string = False): 
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        lge_ex_vol = evaluation.get_volume(0, 'lge_ex')  
        return lge_ex_vol

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff
    

class SCAR_MASS_BF_EX(Clinical_Result):
    def __init__(self):
        self.name = 'SCAR_MASS_BEFORE_EXCL'
        self.unit = '[g]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string = False): 
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        lv_scar_vol_bf_excl = 1.05 * evaluation.get_volume(0, 'lv_scar') + evaluation.get_volume(0, 'lge_ex')  
        return lv_scar_vol_bf_excl

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff





class NR_OF_SLICES_ROI(Clinical_Result):
    def __init__(self):
        self.name = 'NrSlices_Ref'  
        self.unit = '[#]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string = False): 
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        has_myo_ref = False
        has_lge_ref = False
        for d in range(evaluation.nr_slices):
            anno = evaluation.get_anno(d,0)
            if anno.has_contour('myo_ref'): has_myo_ref = True
            elif anno.has_contour('lge_ref'): has_lge_ref = True
        if has_myo_ref and has_lge_ref: return np.nan 
        if not has_myo_ref and not has_lge_ref: return np.nan #für Methoden ohne ROI
        number_of_ROIs = 0
        for d in range(evaluation.nr_slices):
            anno = evaluation.get_anno(d,0)
            number_of_ROIs += int(anno.has_contour('myo_ref') or anno.has_contour('lge_ref'))
            int(anno.has_contour('myo_ref') or anno.has_contour('lge_ref'))
        return number_of_ROIs
        

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class SIZE_ROI(Clinical_Result):
    def __init__(self):
        self.name = 'SIZE_Reference'
        self.unit = '[mm^2]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string = False): 
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        myo_ref_size = 0
        for d in range(evaluation.nr_slices):
            try:    anno = evaluation.get_anno(d,0)
            except: continue
            dcm  = evaluation.get_dcm(d,0)
            pw, ph = evaluation.pixel_w, evaluation.pixel_h
            if anno.has_contour('myo_ref') == True: 
                polygon = anno.get_contour('myo_ref')
                myo_ref_size += polygon.area * (pw * ph)
        
        return myo_ref_size

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff



    
###########
# LAX CRs #
###########
########################
# LV Values:           #
# 4CV / 2CV / Biplane: #
# - ESV, EDV           #
# - SV,  EF            #
########################

#######
# 4CV #
#######
"""
class LAX_4CV_LVESV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_LVESV'
        self.unit = '[ml]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVES_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('lv_lax_endo', self.cat.phase)
        anno = self.cat.get_anno(0, self.cat.phase)
        cr   = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_4CV_LVEDV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_LVEDV'
        self.unit = '[ml]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('lv_lax_endo', self.cat.phase)
        anno = self.cat.get_anno(0, self.cat.phase)
        cr   = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000
        return "{:.2f}".format(cr) if string else cr
        
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_4CV_LVM(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_LVM'
        self.unit = '[g]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVED_Category)][0]
        
    @CR_exception_handler
    def get_val(self, string=False):
        endo_area = self.cat.get_area('lv_lax_endo',  self.cat.phase)
        epi_area  = endo_area + self.cat.get_area('lv_lax_myo',  self.cat.phase)
        L         = self.cat.get_anno(0, self.cat.phase).length_LV()
        endo_area = 8/(3*np.pi) * (endo_area**2)/L / 1000
        epi_area  = 8/(3*np.pi) * (epi_area**2) /L / 1000
        cr        = 1.05 * (epi_area - endo_area)
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff



class LAX_4CV_LVSV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_LVSV'
        self.unit = '[ml]'
        self.cat_es  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVES_Category)][0]
        self.cat_ed  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat_es.get_area('lv_lax_endo', self.cat_es.phase)
        anno = self.cat_es.get_anno(0, self.cat_es.phase)
        esv  = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000
        area = self.cat_ed.get_area('lv_lax_endo', self.cat_ed.phase)
        anno = self.cat_ed.get_anno(0, self.cat_ed.phase)
        edv  = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000
        return "{:.2f}".format(edv - esv) if string else edv - esv

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_4CV_LVEF(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_LVEF'
        self.unit = '[ml]'
        self.cat_es  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVES_Category)][0]
        self.cat_ed  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat_es.get_area('lv_lax_endo', self.cat_es.phase)
        anno = self.cat_es.get_anno(0, self.cat_es.phase)
        esv  = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000
        area = self.cat_ed.get_area('lv_lax_endo', self.cat_ed.phase)
        anno = self.cat_ed.get_anno(0, self.cat_ed.phase)
        edv  = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000 + 10**-9
        return "{:.2f}".format(100.0*(edv-esv)/edv) if string else 100.0*(edv-esv)/edv
    
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_4CV_ESAtrialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_ES_Atrial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVES_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Atrial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_4CV_EDAtrialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_ED_Atrial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Atrial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_4CV_ESEpicardialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_ES_Epicardial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVES_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Epicardial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_4CV_EDEpicardialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_ED_Epicardial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Epicardial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_4CV_ESPericardialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_ES_Pericardial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVES_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Pericardial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_4CV_EDPericardialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_ED_Pericardial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Pericardial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
"""

# Phases
class LAX_4CV_LAESPHASE(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'LAESP_4CV'
        self.unit = '[#]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        vol_curve = np.array([evaluation.get_volume(p, 'la') for p in range(evaluation.nr_phases)])
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        valid_idx = np.where(vol_curve > 0)[0]
        phase = valid_idx[vol_curve[valid_idx].argmin()]
        return str(phase) if string else phase

    def get_val_diff(self, eval1, eval2, string=False):
        p1, p2, nrp = self.get_val(eval1), self.get_val(eval2), eval1.nr_phases
        cr_diff = min(abs(p1-p2), (min(p1,p2) - max(p1,p2)) % nrp) # module ring difference
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
    
# Phases
class LAX_4CV_LAEDPHASE(LAX_4CV_LAESPHASE):
    def set_CR_information(self):
        self.name = 'LAEDP_4CV'
        self.unit = '[#]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        vol_curve = np.array([evaluation.get_volume(p, 'la') for p in range(evaluation.nr_phases)])
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        phase = vol_curve.argmax()
        return str(phase) if string else phase
        
# Phases
class LAX_4CV_RAESPHASE(LAX_4CV_LAESPHASE):
    def set_CR_information(self):
        self.name = 'RAESP_4CV'
        self.unit = '[#]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        vol_curve = np.array([evaluation.get_volume(p, 'ra') for p in range(evaluation.nr_phases)])
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        valid_idx = np.where(vol_curve > 0)[0]
        phase = valid_idx[vol_curve[valid_idx].argmin()]
        return str(phase) if string else phase
        
# Phases
class LAX_4CV_RAEDPHASE(LAX_4CV_LAESPHASE):
    def set_CR_information(self):
        self.name = 'RAEDP_4CV'
        self.unit = '[#]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        vol_curve = np.array([evaluation.get_volume(p, 'ra') for p in range(evaluation.nr_phases)])
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        phase = vol_curve.argmax()
        return str(phase) if string else phase
        
# Phases
class LAX_2CV_LAESPHASE(LAX_4CV_LAESPHASE):
    def set_CR_information(self):
        self.name = 'LAESP_2CV'
        self.unit = '[#]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        vol_curve = np.array([evaluation.get_volume(p, 'la') for p in range(evaluation.nr_phases)])
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        valid_idx = np.where(vol_curve > 0)[0]
        phase = valid_idx[vol_curve[valid_idx].argmin()]
        return str(phase) if string else phase
        
# Phases
class LAX_2CV_LAEDPHASE(LAX_4CV_LAESPHASE):
    def set_CR_information(self):
        self.name = 'LAEDP_2CV'
        self.unit = '[#]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        vol_curve = np.array([evaluation.get_volume(p, 'la') for p in range(evaluation.nr_phases)])
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        phase = vol_curve.argmax()
        return str(phase) if string else phase
    
# Phases
class LAX_2CV_LVESPHASE(LAX_4CV_LAESPHASE):
    def set_CR_information(self):
        self.name = 'LVESP_2CV'
        self.unit = '[#]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        vol_curve = np.array([evaluation.get_volume(p, 'lv_lax_endo') for p in range(evaluation.nr_phases)])
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        valid_idx = np.where(vol_curve > 0)[0]
        phase = valid_idx[vol_curve[valid_idx].argmin()]
        return str(phase) if string else phase
    
# Phases
class LAX_2CV_LVEDPHASE(LAX_4CV_LAESPHASE):
    def set_CR_information(self):
        self.name = 'LVEDP_2CV'
        self.unit = '[#]'
    
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        vol_curve = np.array([evaluation.get_volume(p, 'lv_lax_endo') for p in range(evaluation.nr_phases)])
        has_conts = [a!=0 for a in vol_curve]
        if True not in has_conts: return np.nan
        phase = vol_curve.argmax()
        return str(phase) if string else phase


########
# 2 CV #
########
class LAX_2CV_LVESV(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_LVESV'
        self.unit = '[ml]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    phase = evaluation.clinical_parameters[LAX_2CV_LVESPHASE.__name__]
        except: phase = LAX_2CV_LVESPHASE().get_val(evaluation)
        anno = evaluation.get_anno(0, phase)
        area = anno.get_contour('lv_lax_endo').area * anno.ph * anno.pw
        cr   = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    

class LAX_2CV_LVEDV(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_LVEDV'
        self.unit = '[ml]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        try:    phase = evaluation.clinical_parameters[LAX_2CV_LVEDPHASE.name][0]
        except: phase = LAX_2CV_LVEDPHASE().get_val(evaluation)
        anno = evaluation.get_anno(0, phase)
        area = anno.get_contour('lv_lax_endo').area * anno.ph * anno.pw
        cr   = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    

class LAX_2CV_LVM(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_LVM'
        self.unit = '[g]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        endo_area = self.cat.get_area('lv_lax_endo',  self.cat.phase)
        epi_area  = endo_area + self.cat.get_area('lv_lax_myo',  self.cat.phase)
        L         = self.cat.get_anno(0, self.cat.phase).length_LV()
        endo_area = 8/(3*np.pi) * (endo_area**2)/L / 1000
        epi_area  = 8/(3*np.pi) * (epi_area**2) /L / 1000
        cr        = 1.05 * (epi_area - endo_area)
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_2CV_LVSV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_LVSV'
        self.unit = '[ml]'
        self.cat_es  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVES_Category)][0]
        self.cat_ed  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat_es.get_area('lv_lax_endo', self.cat_es.phase)
        anno = self.cat_es.get_anno(0, self.cat_es.phase)
        esv  = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000
        area = self.cat_ed.get_area('lv_lax_endo', self.cat_ed.phase)
        anno = self.cat_ed.get_anno(0, self.cat_ed.phase)
        edv  = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000
        return "{:.2f}".format(edv - esv) if string else edv - esv

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_2CV_LVEF(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_LVEF'
        self.unit = '[ml]'
        self.cat_es  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVES_Category)][0]
        self.cat_ed  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat_es.get_area('lv_lax_endo', self.cat_es.phase)
        anno = self.cat_es.get_anno(0, self.cat_es.phase)
        esv  = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000
        area = self.cat_ed.get_area('lv_lax_endo', self.cat_ed.phase)
        anno = self.cat_ed.get_anno(0, self.cat_ed.phase)
        edv  = 8/(3*np.pi) * (area**2)/anno.length_LV() / 1000 + 10**-9
        return "{:.2f}".format(100.0*(edv-esv)/edv) if string else 100.0*(edv-esv)/edv

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    

class LAX_2CV_ESAtrialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_ES_Atrial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVES_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Atrial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_2CV_EDAtrialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_ED_Atrial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Atrial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff    

class LAX_2CV_ESEpicardialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_ES_Epicardial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVES_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Epicardial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_2CV_EDEpicardialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_ED_Epicardial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Epicardial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_2CV_ESPericardialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_ES_Pericardial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVES_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Pericardial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_2CV_EDPericardialFatArea(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_ED_Pericardial_Fat_Area'
        self.unit = '[cm^2]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('Pericardial', self.cat.phase)
        area = area / 100.0
        return "{:.2f}".format(area) if string else area

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

###########
# Biplane #
###########
"""
class LAX_BIPLANE_LVESV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'BIPLANE_LVESV'
        self.unit = '[ml]'
        self.cat1 = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVES_Category)][0]
        self.cat2 = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVES_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area1 = self.cat1.get_area('lv_lax_endo', self.cat1.phase)
        area2 = self.cat2.get_area('lv_lax_endo', self.cat2.phase)
        anno1 = self.cat1.get_anno(0, self.cat1.phase)
        anno2 = self.cat2.get_anno(0, self.cat2.phase)
        L     = min(anno1.length_LV(), anno2.length_LV())
        cr    = 8/(3*np.pi) * (area1*area2)/L / 1000
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class LAX_BIPLANE_LVEDV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'BIPLANE_LVEDV'
        self.unit = '[ml]'
        self.cat1 = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVED_Category)][0]
        self.cat2 = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area1 = self.cat1.get_area('lv_lax_endo', self.cat1.phase)
        area2 = self.cat2.get_area('lv_lax_endo', self.cat2.phase)
        anno1 = self.cat1.get_anno(0, self.cat1.phase)
        anno2 = self.cat2.get_anno(0, self.cat2.phase)
        L     = min(anno1.length_LV(), anno2.length_LV())
        cr    = 8/(3*np.pi) * (area1*area2)/L / 1000
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_BIPLANE_LVSV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'BIPLANE_LVSV'
        self.unit = '[ml]'
        self.cates1 = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVES_Category)][0]
        self.cates2 = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVES_Category)][0]
        self.cated1 = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVED_Category)][0]
        self.cated2 = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area1 = self.cates1.get_area('lv_lax_endo', self.cates1.phase)
        area2 = self.cates2.get_area('lv_lax_endo', self.cates2.phase)
        anno1 = self.cates1.get_anno(0, self.cates1.phase)
        anno2 = self.cates2.get_anno(0, self.cates2.phase)
        L     = min(anno1.length_LV(), anno2.length_LV())
        esv   = 8/(3*np.pi) * (area1*area2)/L / 1000
        area1 = self.cated1.get_area('lv_lax_endo', self.cated1.phase)
        area2 = self.cated2.get_area('lv_lax_endo', self.cated2.phase)
        anno1 = self.cated1.get_anno(0, self.cated1.phase)
        anno2 = self.cated2.get_anno(0, self.cated2.phase)
        L     = min(anno1.length_LV(), anno2.length_LV())
        edv   = 8/(3*np.pi) * (area1*area2)/L / 1000
        cr    = edv - esv
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_BIPLANE_LVEF(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = 'BIPLANE_LVEF'
        self.unit = '[ml]'
        self.cates1 = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVES_Category)][0]
        self.cates2 = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVES_Category)][0]
        self.cated1 = [c for c in self.case.categories if isinstance(c, LAX_2CV_LVED_Category)][0]
        self.cated2 = [c for c in self.case.categories if isinstance(c, LAX_4CV_LVED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area1 = self.cates1.get_area('lv_lax_endo', self.cates1.phase)
        area2 = self.cates2.get_area('lv_lax_endo', self.cates2.phase)
        anno1 = self.cates1.get_anno(0, self.cates1.phase)
        anno2 = self.cates2.get_anno(0, self.cates2.phase)
        L     = min(anno1.length_LV(), anno2.length_LV())
        esv   = 8/(3*np.pi) * (area1*area2)/L / 1000
        area1 = self.cated1.get_area('lv_lax_endo', self.cated1.phase)
        area2 = self.cated2.get_area('lv_lax_endo', self.cated2.phase)
        anno1 = self.cated1.get_anno(0, self.cated1.phase)
        anno2 = self.cated2.get_anno(0, self.cated2.phase)
        L     = min(anno1.length_LV(), anno2.length_LV())
        edv   = 8/(3*np.pi) * (area1*area2)/L / 1000 + 10**-9
        cr    = 100.0 * (edv - esv) / edv
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
"""
    
################
# Right Atrium #
# - 4CV area   #
# - 4CV volume #
################

class LAX_4CV_RAESAREA(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_RAESAREA'
        self.unit = '[cm^2]'

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    phase = evaluation.clinical_parameters[LAX_4CV_RAESPHASE.__name__][0]
        except: phase = LAX_4CV_RAESPHASE().get_val(evaluation)
        anno = evaluation.get_anno(0, phase)
        cr = anno.get_contour('ra').area * anno.ph * anno.pw / 100.0
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_4CV_RAEDAREA(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_RAEDAREA'
        self.unit = '[cm^2]'
        self.tol_range = 1.0

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    phase = evaluation.clinical_parameters[LAX_4CV_RAEDPHASE.__name__][0]
        except: phase = LAX_4CV_RAEDPHASE().get_val(evaluation)
        anno = evaluation.get_anno(0, phase)
        cr = anno.get_contour('ra').area * anno.ph * anno.pw / 100.0
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

"""
class LAX_4CV_RAESV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_RAESV'
        self.unit = '[ml]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_RAES_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('ra', self.cat.phase)
        anno = self.cat.get_anno(0, self.cat.phase)
        cr   = 8/(3*np.pi) * (area**2)/anno.length_RA() / 1000
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_4CV_RAEDV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_RAEDV'
        self.unit = '[ml]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_RAED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('ra', self.cat.phase)
        anno = self.cat.get_anno(0, self.cat.phase)
        cr   = 8/(3*np.pi) * (area**2)/anno.length_RA() / 1000
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
"""
    
############
# LA 4CV   #
# - Area   #
# - Volume #
############
class LAX_4CV_LAESAREA(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_LAESAREA'
        self.unit = '[cm^2]'
        
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    phase = evaluation.clinical_parameters[LAX_4CV_LAESPHASE.__name__][0]
        except: phase = LAX_4CV_LAESPHASE().get_val(evaluation)
        anno = evaluation.get_anno(0, phase)
        cr = anno.get_contour('la').area * anno.ph * anno.pw / 100.0
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff
    

class LAX_4CV_LAEDAREA(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_LAEDAREA'
        self.unit = '[cm^2]'
        self.tol_range = 2.1
        
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    phase = evaluation.clinical_parameters[LAX_4CV_LAEDPHASE.__name__][0]
        except: phase = LAX_4CV_LAEDPHASE().get_val(evaluation)
        anno = evaluation.get_anno(0, phase)
        cr = anno.get_contour('la').area * anno.ph * anno.pw / 100.0
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

"""
class LAX_4CV_LAESV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_LAESV'
        self.unit = '[ml]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LAES_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('la', self.cat.phase)
        anno = self.cat.get_anno(0, self.cat.phase)
        cr   = 8/(3*np.pi) * (area**2)/anno.length_LA() / 1000
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_4CV_LAEDV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '4CV_LAEDV'
        self.unit = '[ml]'
        self.cat  = [c for c in self.case.categories if isinstance(c, LAX_4CV_LAED_Category)][0]

    @CR_exception_handler
    def get_val(self, string=False):
        area = self.cat.get_area('la', self.cat.phase)
        anno = self.cat.get_anno(0, self.cat.phase)
        cr   = 8/(3*np.pi) * (area**2)/anno.length_LA() / 1000
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
"""

############
# LA 2CV   #
# - Area   #
# - Volume #
############
class LAX_2CV_LAESAREA(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_LAESAREA'
        self.unit = '[cm^2]'
        
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    phase = evaluation.clinical_parameters[LAX_2CV_LAESPHASE.__name__][0]
        except: phase = LAX_2CV_LAESPHASE().get_val(evaluation)
        anno = evaluation.get_anno(0, phase)
        cr = anno.get_contour('la').area * anno.ph * anno.pw / 100.0
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff
    

class LAX_2CV_LAEDAREA(Clinical_Result):
    def __init__(self):
        self.set_CR_information()

    def set_CR_information(self):
        self.name = '2CV_LAEDAREA'
        self.unit = '[cm^2]'
        self.tol_range = 2.0

    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    phase = evaluation.clinical_parameters[LAX_2CV_LAEDPHASE.__name__][0]
        except: phase = LAX_2CV_LAEDPHASE().get_val(evaluation)
        anno = evaluation.get_anno(0, phase)
        cr = anno.get_contour('la').area * anno.ph * anno.pw / 100.0
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff


###############
# LA Biplanar #
# - Volume    #
###############
"""
class LAX_BIPLANAR_LAESV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'BIPLANE_LAESV'
        self.unit = '[ml]'
        self.cat1 = [c for c in self.case.categories if isinstance(c, LAX_2CV_LAES_Category)][0]
        self.cat2 = [c for c in self.case.categories if isinstance(c, LAX_4CV_LAES_Category)][0]
        
    @CR_exception_handler
    def get_val(self, string=False):
        area1 = self.cat1.get_area('la', self.cat1.phase)
        L1    = self.cat1.get_anno(0, self.cat1.phase).length_LA()
        area2 = self.cat2.get_area('la', self.cat2.phase)
        L2    = self.cat2.get_anno(0, self.cat2.phase).length_LA()
        L     = min(L1, L2)
        cr    = 8/(3*np.pi) * (area1*area2)/L / 1000
        return "{:.2f}".format(cr) if string else cr

    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class LAX_BIPLANAR_LAEDV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'BIPLANE_LAEDV'
        self.unit = '[ml]'
        self.cat1 = [c for c in self.case.categories if isinstance(c, LAX_2CV_LAED_Category)][0]
        self.cat2 = [c for c in self.case.categories if isinstance(c, LAX_4CV_LAED_Category)][0]
        
    @CR_exception_handler
    def get_val(self, string=False):
        area1 = self.cat1.get_area('la', self.cat1.phase)
        L1    = self.cat1.get_anno(0, self.cat1.phase).length_LA()
        area2 = self.cat2.get_area('la', self.cat2.phase)
        L2    = self.cat2.get_anno(0, self.cat2.phase).length_LA()
        L     = min(L1, L2)
        cr    = 8/(3*np.pi) * (area1*area2)/L / 1000
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
"""

###############
# CRs Mapping #
###############
class SAXMap_GLOBALT1_PRE(Clinical_Result):
    def __init__(self):
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'GLOBAL_T1'
        self.unit = '[ms]'
        self.tol_range = 24.5
        
    @CR_exception_handler
    def get_val(self, evaluation, string=False):
        try:    return evaluation.clinical_parameters[self.name][0]
        except: pass
        cr = []
        for d in range(evaluation.nr_slices):
            try: cr += evaluation.get_anno(d,0).get_pixel_values('lv_myo', evaluation.get_img(d,0)).tolist()
            except: print(traceback.format_exc()); continue
        cr = np.nanmean(cr)
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, eval1, eval2, string=False):
        cr_diff = self.get_val(eval1)-self.get_val(eval2)
        return "{:.2f}".format(cr_diff) if string else cr_diff

    
    
class SAXMap_GLOBALT1_POST(SAXMap_GLOBALT1_PRE):
    def __init__(self):
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'GLOBAL_T1'
        self.unit = '[ms]'
        self.tol_range = 6.2
        

class SAXMap_GLOBALT2(SAXMap_GLOBALT1_PRE):
    def __init__(self):
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'GLOBAL_T2'
        self.unit = '[ms]'
        self.tol_range = 3.2
        

class SAXLGE_LVV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'LVV'
        self.unit = '[ml]'
        self.cat  = self.case.categories[0]
    
    @CR_exception_handler
    def get_val(self, string=False):
        cr = self.cat.get_volume('lv_endo')
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
"""
class SAXLGE_LVMYOMASS(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'LVM'
        self.unit = '[g]'
        #self.cat  = [c for c in self.case.categories if isinstance(c, SAX_LGE_Category)][0]
        self.cat  = self.case.categories[0]
        
    @CR_exception_handler
    def get_val(self, string=False):
        cr = 1.05 * self.cat.get_volume('lv_myo')
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class SAXLGE_LVMYOV(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'LVMV'
        self.unit = '[ml]'
        #self.cat  = [c for c in self.case.categories if isinstance(c, SAX_LGE_Category)][0]
        self.cat  = self.case.categories[0]
        
    @CR_exception_handler
    def get_val(self, string=False):
        cr = self.cat.get_volume('lv_myo')
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff

class SAXLGE_SCARMASS(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'SCARM'
        self.unit = '[g]'
        #self.cat  = [c for c in self.case.categories if isinstance(c, SAX_LGE_Category)][0]
        self.cat  = self.case.categories[0]
        
    @CR_exception_handler
    def get_val(self, contname='scar', string=False):
        #cr = 1.05 * self.cat.get_volume('scar_fwhm_res_8_excluded_area')
        cr = 1.05 * self.cat.get_volume(contname)
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, contname='scar', string=False):
        cr_diff = self.get_val(contname)-other.get_val(contname)
        return "{:.2f}".format(cr_diff) if string else cr_diff

class SAXLGE_SCARVOL(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'SCARV'
        self.unit = '[ml]'
        #self.cat  = [c for c in self.case.categories if isinstance(c, SAX_LGE_Category)][0]
        self.cat  = self.case.categories[0]
        
    @CR_exception_handler
    def get_val(self, contname='scar', string=False):
        #cr = self.cat.get_volume('scar_fwhm_res_8_excluded_area')
        cr = self.cat.get_volume(contname)
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, contname='scar', string=False):
        cr_diff = self.get_val(contname)-other.get_val(contname)
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class SAXLGE_SCARF(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'SCARF'
        self.unit = '[%]'
        #self.cat  = [c for c in self.case.categories if isinstance(c, SAX_LGE_Category)][0]
        self.cat  = self.case.categories[0]
        
    @CR_exception_handler
    def get_val(self, contname='scar', string=False):
        scar = self.cat.get_volume(contname)
        lvm  = self.cat.get_volume('lv_myo')
        cr = 100.0 * (scar/(lvm+10**-9))
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, contname='scar', string=False):
        cr_diff = self.get_val(contname)-other.get_val(contname)
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
class SAXLGE_EXCLMASS(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'EXCLMASS'
        self.unit = '[g]'
        #self.cat  = [c for c in self.case.categories if isinstance(c, SAX_LGE_Category)][0]
        self.cat  = self.case.categories[0]
        
    @CR_exception_handler
    def get_val(self, string=False):
        scar_excl = self.cat.get_volume('scar_fwhm_excluded_area')
        scar      = self.cat.get_volume('scar_fwhm')
        cr = 1.05 * (scar - scar_excl)
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
    
class SAXLGE_EXCLVOL(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'EXCLVOL'
        self.unit = '[ml]'
        #self.cat  = [c for c in self.case.categories if isinstance(c, SAX_LGE_Category)][0]
        self.cat  = self.case.categories[0]
    
    @CR_exception_handler
    def get_val(self, string=False):
        scar_excl = self.cat.get_volume('scar_fwhm_res_8_excluded_area')
        scar      = self.cat.get_volume('scar_fwhm_res_8')
        cr = scar - scar_excl
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
            
    
class SAXLGE_NOREFLOWVOL(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'NOREFLOWVOL'
        self.unit = '[ml]'
        #self.cat  = [c for c in self.case.categories if isinstance(c, SAX_LGE_Category)][0]
        self.cat  = self.case.categories[0]
        
    @CR_exception_handler
    def get_val(self, string=False):
        cr = self.cat.get_volume('noreflow')
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
    
    
class SAXLGE_NOREFLOWF(Clinical_Result):
    def __init__(self, case):
        self.case = case
        self.set_CR_information()
        
    def set_CR_information(self):
        self.name = 'NOREFLOWF'
        self.unit = '[%]'
        #self.cat  = [c for c in self.case.categories if isinstance(c, SAX_LGE_Category)][0]
        self.cat  = self.case.categories[0]
        
    @CR_exception_handler
    def get_val(self, contname='noreflow', string=False):
        scar = self.cat.get_volume(contname)
        lvm  = self.cat.get_volume('lv_myo')
        cr = 100.0 * (scar/(lvm+10**-9))
        return "{:.2f}".format(cr) if string else cr
    
    def get_val_diff(self, other, string=False):
        cr_diff = self.get_val()-other.get_val()
        return "{:.2f}".format(cr_diff) if string else cr_diff
"""