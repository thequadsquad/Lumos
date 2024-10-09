from RoomOfRequirement.ClinicalResults import *
from RoomOfRequirement.Views.SaxCineView import SAX_CINE_View

from RoomOfRequirement.Tables  import *
from RoomOfRequirement.Figures import *

import traceback


class SAX_CS_View(SAX_CINE_View):
    def __init__(self):
        super().__init__()
        self.name = 'SAX CS'
        self.cmap = 'gray'
