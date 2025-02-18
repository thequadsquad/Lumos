from Lumos.ClinicalResults import *
from Lumos.Views.SaxCineView import SAX_CINE_View

from Lumos.Tables  import *
from Lumos.Figures import *

import traceback


class SAX_CS_View(SAX_CINE_View):
    def __init__(self):
        super().__init__()
        self.name = 'SAX CS'
        self.cmap = 'gray'
