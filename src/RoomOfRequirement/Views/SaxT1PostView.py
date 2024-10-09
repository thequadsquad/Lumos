from RoomOfRequirement.ClinicalResults import *
from RoomOfRequirement.Views.SaxT1PreView import SAX_T1_PRE_View

from RoomOfRequirement.Tables  import *
from RoomOfRequirement.Figures import *

import traceback


class SAX_T1_POST_View(SAX_T1_PRE_View):
    def __init__(self):
        super().__init__()
        self.name   = 'SAX T1 POST'
        
        self.cmap = 'gray'
        
        self.clinical_results = [SAXMap_GLOBALT1_POST, NR_SLICES]
    