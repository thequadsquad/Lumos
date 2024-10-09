from RoomOfRequirement.ClinicalResults import *
from RoomOfRequirement.Views.View import *

from RoomOfRequirement.Tables  import *
from RoomOfRequirement.Figures import *

import traceback

import csv
import PIL


class SAX_LGE_View(View):
    def __init__(self):
        self.name = 'SAX LGE'
        self.cmap = 'gray'
        
        self.contour_names = ['lv_myo', 'lv_endo', 'lv_scar', 'myo_ref', 'lge_ref', 'noreflow', 'lge_ex']
        
        self.clinical_parameters = [cr() for cr in [MYO_MASS, SCAR_MASS, SCAR_PCT, EX_VOL, SCAR_MASS_BF_EX, NR_SLICES, NR_OF_SLICES_ROI, SIZE_ROI]]
        self.clinical_parameters = {cr.name: cr for cr in self.clinical_parameters}
        
        # register tabs here:
        import RoomOfRequirement.Guis.Addable_Tabs.CC_Metrics_Tab                   as tab1
        import RoomOfRequirement.Guis.Addable_Tabs.CCs_ClinicalResults_Tab          as tab2
        import RoomOfRequirement.Guis.Addable_Tabs.CC_Overview_Tab                  as tab4

        import RoomOfRequirement.Guis.Addable_Tabs.CC_LGE_Metrics_Histos_Tab        as tab5
        import RoomOfRequirement.Guis.Addable_Tabs.CCs_CRs_OverviewTable_Tab        as tab6
        import RoomOfRequirement.Guis.Addable_Tabs.CCs_Metrics_OverviewTable_Tab    as tab7

        import RoomOfRequirement.Guis.Addable_Tabs.MULTI_ClinicalResults_Tab        as tab8
        import RoomOfRequirement.Guis.Addable_Tabs.MULTI_Histos_Tab                 as tab9
        import RoomOfRequirement.Guis.Addable_Tabs.MULTI_Annos_Figure_Tab           as tab10
        
       
        #tabs for two reader comparison
        self.case_tabs        = {'Metrics and Figure'   : tab1.CC_Metrics_Tab,            'Clinical Results and Images'    : tab4.CC_CRs_Images_Tab,         'Metrics, Figure and Histograms': tab5.CC_LGE_Metrics_Histos_Tab}
        self.stats_tabs       = {'Clinical Results'     : tab2.CCs_ClinicalResults_Tab,   'Clinical Results Overview Table': tab6.CCs_CRs_OverviewTable_Tab, 'Metrics Overview Table'        : tab7.CCs_Metrics_OverviewTable_Tab}

        #tabs for multi reader comparison
        self.multi_case_tabs  = {'Figures and Histograms': tab9.Multi_LGE_Histos_Tab, 'Multi Anno Figure and Clinical Results': tab10.Multi_Annos_One_Figure_Tab}
        self.multi_stats_tabs = {'Clinical Results'      : tab8.Multi_ClinicalResults_Tab}

    