import pandas
from pandas import DataFrame
import traceback

from RoomOfRequirement.Tables.Table import *
from RoomOfRequirement.loading_functions import *
from RoomOfRequirement.Metrics import *
from RoomOfRequirement.Tables.T1_CC_Metrics_Table import *

        
class T2_CC_Metrics_Table(T1_CC_Metrics_Table):
    def get_column_names(self, cat):
        n = cat.name
        return [n+' Area Diff', n+' DSC', n+' HD', n+' T2avg_r1', n+' T2avg_r2', n+' T2avgDiff', n+' AngleDiff', n+' hascont1', n+' hascont2']