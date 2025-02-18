from time import time

import numpy as np
from scipy.ndimage import morphology
from shapely.geometry import Polygon, MultiPolygon, LineString, GeometryCollection, Point, MultiPoint, shape
from skimage.measure import find_contours
from rasterio import features
import pydicom

from PIL import Image, ImageDraw
from matplotlib.patches import PathPatch
import matplotlib
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import QMainWindow, QApplication
from matplotlib.backends import backend_qt as mpl_backend



#####################
# Dicom Tag to Name #
#####################
dcmtag2name =   {'0x0080018': 'sop',                       '0x0080020': 'studydate', 
                 '0x0080030': 'studytime',                 '0x0080070': 'manufacturer',
                 '0x0080080': 'institutionname',           '0x0081030': 'studydescription', 
                 '0x008103e': 'seriesdescription',         '0x0081090': 'manufacturermodelname', 
                 '0x00b0010': 'imagetype',                 '0x0100010': 'name',
                 '0x0100020': 'patient_id',                '0x0100030': 'birthdate',
                 '0x0100040': 'sex',                       '0x0101010': 'age',
                 '0x0101020': 'size',                      '0x0101030': 'weight',
                 '0x0180015': 'bodypart',                  '0x0180024': 'sequencename',
                 '0x0180025': 'angioflag',                 '0x0180050': 'slicethickness',
                 '0x0180087': 'magneticfieldstrength',     '0x0180088': 'spacingbetweenslices',
                 '0x0181020': 'softwareversions',          '0x0181030': 'protocolname',
                 '0x0181314': 'flipangle',                 '0x0181315': 'variableflipangleflag',
                 '0x0185100': 'patient_position',          '0x020000d': 'studyuid',
                 '0x020000e': 'seriesuid',                 '0x0200010': 'study_id',
                 '0x0200011': 'seriesnumber',              '0x0200012': 'acquisitionnumber',
                 '0x0200013': 'instancenumber',            '0x0200032': 'imageposition_patient',
                 '0x0200037': 'imageorientation_patient',  '0x0201041': 'slicelocation',
                 '0x0204000': 'imagecomments',             '0x0280010': 'rows',
                 '0x0280011': 'columns',                   '0x0280030': 'pixelspacing',
                 '0x0280106': 'smallestimagepixelvalue',   '0x0280107': 'largestimagepixelvalue',
                 '0x0281050': 'windowcenter',              '0x0281051': 'windowwidth'}

def dcmvalue2pythontype(key, val):
    vtype = type(val)
    if vtype in [pydicom.uid.UID, pydicom.valuerep.PersonName]: return str(val)
    if vtype in [pydicom.valuerep.IS]:                          return int(val)
    if vtype in [pydicom.valuerep.DSfloat]:                     return float(val)
    if vtype in [pydicom.multival.MultiValue]:                  return [float(v) for v in val]
    if key.lower().endswith('date'): return str(date(year=int(val[:4]), month=int(val[4:6]), day=int(val[6:])))
    if key=='imagetype': 
        val = val.replace('Lazy Luna: ', '')
        if val=='None': val='Unknown'
    return val

def dcm_to_json(dcm, path):
    json_dict = {'path': path}
    for tag,name in dcmtag2name.items():
        try: json_dict[name] = dcmvalue2pythontype(name, dcm[tag].value)
        except Exception as e: continue
    return json_dict

###################
# unpack dcm json #
###################
"""
def unpack_dcm(dcm_json):
    fmeta = dcm_json['file_meta']
    for k in ['_id', 'file_meta', 'sop', 'imagetype', 'seriesuid', 'studyuid', 'seriesdescription']: dcm_json.pop(k, None)
    dcm = pydicom.dataset.Dataset.from_json(dcm_json)
    dcm.ensure_file_meta()
    dcm.file_meta = pydicom.dataset.FileMetaDataset.from_json(fmeta)
    dcm.preamble = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    return dcm
"""


##################
# Mask functions #
##################

def to_mask(polygons, height, width):
    """Convert to mask (Origin (0.0, 0.0))
    
    Note:
        rasterio.features.rasterize(shapes, out_shape=None, fill=0, out=None, transform=Affine(1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
        all_touched=False, merge_alg=MergeAlg.replace, default_value=1, dtype=None)
        For Origin (-0.5, -0.5) apply Affine Transformation (1.0, 0.0, -0.5, 0.0, 1.0, -0.5)
        https://rasterio.readthedocs.io/en/latest/api/rasterio.features.html#rasterio.features.rasterize
        
    Args:
        polygons (shapely.geometry. Polygon | Multipolygon): geometry to be burned into mask
        height (int): output mask height
        width (int):  output mask width
        
    Returns:
        ndarray (2D array of np.uint8): binarized mask of polygon
    """
    if not isinstance(polygons, list):
        if isinstance(polygons, Polygon) or isinstance(polygons, MultiPolygon): polygons = [polygons]
        else: raise Exception('to_mask accepts a List of Polygons or Multipolygons')
    if len(polygons) > 0:
        try: mask = features.rasterize(polygons, out_shape=(height, width), dtype=np.uint8)
        except Exception as e:
            mask = np.zeros((height, width), np.uint8)
            print(str(e) + ', returning empty mask.')
    else: mask = np.zeros((height, width), np.uint8)
    return mask

def to_mask_pct(geo, height, width): 
    """Convert geo to mask (Origin (0.0, 0.0)) with exact percentage of pixels
        see: https://gist.github.com/perrygeo/721040f8545272832a42#file-rasterize-py
        
    Note:
        rasterio.features.rasterize(shapes, out_shape=None, fill=0, out=None, transform=Affine(1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
        all_touched=False, merge_alg=MergeAlg.replace, default_value=1, dtype=None)
        For Origin (-0.5, -0.5) apply Affine Transformation (1.0, 0.0, -0.5, 0.0, 1.0, -0.5)
        https://rasterio.readthedocs.io/en/latest/api/rasterio.features.html#rasterio.features.rasterize
        
    Args:
        geo (shapely.geometry. Polygon | Multipolygon): geometry to be burned into mask
        height (int): output mask height
        width (int):  output mask width
        
    Returns:
        ndarray (2D array): mask of polygon with values between 0 and 1
    """
    size = (width, height)  
    #geo  = shape(polygons)
    try: 
        if geo.geom_type == 'Polygon':    
            alltouched = rio.features.rasterize([geo], size, all_touched=True)
            exterior = rio.features.rasterize([geo.exterior, *geo.interiors], size, all_touched=True)
            # Create percent cover grid as the difference between them
            # at this point all cells are known 100% coverage,
            # we'll update this array for exterior points
            pctcover = (alltouched - exterior).astype(np.float32)
            # loop through indicies of all exterior cells
            for r, c in zip(*np.where(exterior == 1)):
                # Find cell bounds, from rasterio DatasetReader.window_bounds
                window = ((r, r+1), (c, c+1))
                ((row_min, row_max), (col_min, col_max)) = window
                bounds = (col_min, row_max, col_max, row_min)
                # Construct shapely geometry of cell
                cell = box(*bounds)
                # Intersect with original shape
                cell_overlap = cell.intersection(geo)
                # update pctcover with percentage based on area proportion
                coverage = cell_overlap.area / cell.area
                pctcover[r, c] = coverage       
            mask = pctcover
        pctdict = {}
        if geo.geom_type == 'MultiPolygon':   
            for g in range(0, len(geo.geoms)):
                geo_multi = geo.geoms[g]
                alltouched = rio.features.rasterize([geo_multi], size, all_touched=True)
                exterior = rio.features.rasterize([geo_multi.exterior, *geo_multi.interiors], size, all_touched=True)
                pctcover = (alltouched - exterior).astype(np.float32)
                for r, c in zip(*np.where(exterior == 1)):
                    # Find cell bounds, from rasterio DatasetReader.window_bounds
                    window = ((r, r+1), (c, c+1))
                    ((row_min, row_max), (col_min, col_max)) = window
                    bounds = (col_min, row_max, col_max, row_min)
                    # Construct shapely geometry of cell
                    cell = box(*bounds)
                    # Intersect with original shape
                    cell_overlap = cell.intersection(geo_multi)
                    # update pctcover with percentage based on area proportion
                    coverage = cell_overlap.area / cell.area
                    pctcover[r, c] = coverage 
                pctdict[geo_multi] = pctcover
            pctmultigeo = np.zeros(size)
            for value in pctdict.values():
                #print(value)
                pctmultigeo += value
            mask = pctmultigeo
    except Exception as e:
        mask = np.zeros((width, height), np.uint8)
        print(str(e) + ', returning empty mask.')
    return mask

def to_polygon(mask):
    """Convert mask to Polygons (Origin (0.0, 0.0))
    
    Note:
        rasterio.features.shapes(source, mask=None, connectivity=4, transform=Affine(1.0, 0.0, 0.0, 0.0, 1.0, 0.0))
        For Origin (-0.5, -0.5) apply Polygon Transformation -0.5 for all xy
        https://rasterio.readthedocs.io/en/latest/api/rasterio.features.html#rasterio.features.shapes
        
    Args:
        mask (ndarray (2D array of np.uint8): binary mask
        
    Returns:
        MultiPolygon | Polygon: Geometries extracted from mask, empty Polygon if empty mask
    """
    polygons = []
    for geom, val in features.shapes(mask):
        if val:
            polygon = shape(geom)
            if polygon.geom_type == 'Polygon' and polygon.is_valid: polygons.append(polygon)
            else: print('Ignoring GeoJSON with cooresponding shape: ' + 
                      str(polygon.geom_type) + ' | Valid: ' + str(polygon.is_valid))
    return MultiPolygon(polygons) if len(polygons)>0 else Polygon()#polygons[0]



####################
# Metric functions #
####################

def dice(geo1, geo2):
    """Calculates Dice metric value
    
    Args:
        geo1 (shapely.geometry): Like a Polygon, Multipolygon, GeometryCollection (containing LineStrings)
        geo2 (shapely.geometry): Like a Polygon, Multipolygon, GeometryCollection (containing LineStrings)
        
    Returns:
        float: Dice value in [0, 100]%
    """
    if geo1.is_empty and geo2.is_empty: return 100.0
    overlap = geo1.intersection(geo2)
    return 100.0 * (2*overlap.area) / (geo1.area + geo2.area)

def hausdorff(geo1, geo2):
    """Calculates Hausdorff distance
    
    Note:
        - if both geometries are empty: HD = 0
        - if only one is empty: HD = np.nan
        - otherwise regular definition
    
    Args:
        geo1 (shapely.geometry): Like a Polygon, Multipolygon, GeometryCollection (containing LineStrings)
        geo2 (shapely.geometry): Like a Polygon, Multipolygon, GeometryCollection (containing LineStrings)
        
    Returns:
        float: Hausdorff distance value
    """
    if geo1.is_empty and geo2.is_empty: return 0.0
    return geo1.hausdorff_distance(geo2)


#######################
# geometry operations #
#######################
def get_overlapping_geometry(geo1, geo2):
    """get intersection"""
    overlap = geo1.intersection(geo2)
    if overlap.is_empty: overlap = Polygon([])
    return overlap

def get_geometry_diff1(geo1, geo2):
    """get difference"""
    diff = geo1.difference(geo2)
    return diff
    
def get_geometry_diff2(geo1, geo2):
    """get difference"""
    return get_geometry_diff1(geo2, geo1)

# convenience function
def get_geometry_comparison(geo1, geo2):
    """returns (intersection(geo1, geo2), difference(geo1,geo2), difference(geo2,geo1))"""
    overlapping = get_overlapping_geometry(geo1, geo2)
    diff1 = get_geometry_diff1(geo1, geo2)
    diff2 = get_geometry_diff2(geo1, geo2)
    return overlapping, diff1, diff2



#####################
# plotting funtions #
#####################

def PolygonPatch_Outline(polygon, c=(1,1,1,1.0), alpha=1.0):
    return PathPatch(matplotlib.path.Path.make_compound_path(matplotlib.path.Path(np.asarray(polygon.exterior.coords)[:,:2]), *[matplotlib.path.Path(np.asarray(ring.coords)[:,:2]) for ring in polygon.interiors]), ec=c, alpha=alpha, fill=False)

def PolygonPatch(polygon, c=None, alpha=1.0):
    return PathPatch(matplotlib.path.Path.make_compound_path(
        matplotlib.path.Path(np.asarray(polygon.exterior.coords)[:, :2]),
        *[matplotlib.path.Path(np.asarray(ring.coords)[:, :2]) for ring in polygon.interiors]
    ), fc=c, linewidth=0, alpha=alpha, zorder=1)


def plot_outlines(ax, geo, c=(1,1,1,1.0)):
    """plots geometry outlines onto matplotlib.pyplot.axis"""
    if geo.geom_type=='Polygon': ax.add_patch(PolygonPatch_Outline(geo, c=c))
    if geo.geom_type=='MultiPolygon':
        for p in geo.geoms:      ax.add_patch(PolygonPatch_Outline(p,   c=c))
        
        
def plot_geo_face_comparison(ax, geo1, geo2, colors=['g','r','b'], alpha=0.4):
    """plots geometry surface comparison onto matplotlib.pyplot.axis"""
    agreed, diff1, diff2 = get_geometry_comparison(geo1, geo2)
    if agreed.geom_type=='GeometryCollection' and not agreed.is_empty:
        agreed = MultiPolygon([g for g in agreed.geoms if g.area!=0])
    if diff1.geom_type=='GeometryCollection' and not diff1.is_empty:
        diff1 = MultiPolygon([g for g in diff1.geoms if g.area!=0])
    if diff2.geom_type=='GeometryCollection' and not diff2.is_empty:
        diff2 = MultiPolygon([g for g in diff2.geoms if g.area!=0])
    for i, thing in enumerate([agreed, diff1, diff2]):
        if not thing.is_empty:
            if thing.geom_type=='Polygon': ax.add_patch(PolygonPatch(thing, c=colors[i], alpha=alpha))
            if thing.geom_type=='MultiPolygon':
                for p in thing.geoms:      ax.add_patch(PolygonPatch(p,     c=colors[i], alpha=alpha))
    
def plot_geo_face(ax, geo, c='r', alpha=0.4):
    """plots geometry surface onto matplotlib.pyplot.axis"""
    if geo.geom_type=='Polygon': ax.add_patch(PolygonPatch(geo, c=c, alpha=alpha))
    if geo.geom_type=='MultiPolygon':
        for p in geo.geoms:      ax.add_patch(PolygonPatch(p,   c=c, alpha=alpha))
        
def plot_points(ax, points, c='w', marker='x', s=None):
    """plots points onto matplotlib.pyplot.axis"""
    if points.geom_type=='Point': # case: points is really just point
        ax.scatter(points.x, points.y, c=c, marker=marker, s=s)
        return
    xs, ys = [point.x for point in points.geoms], [point.y for point in points.geoms]
    ax.scatter(xs, ys, c=c, marker=marker, s=s)
    
    
##############################
## Spatial Dicom Operations ##
##############################
def transform_ics_to_rcs(dcm, arr_points=None):
    """Transforms points on the dcm image (in ics) into points in a 3D reference coordinate system (rcs)
    
    Notes:
        ics = image coordinate system (tupel of x-, y-values in units of pixel in dicom pixel data x=column, y=row)
        rcs = reference coordinate system (standard to store points in dicom tags)
        Function to transform ics -> rcs in dependence of arr_points
        
    Args:
        dcm (dicom dataset): input dicom dataset with attributes to calculate basis transformation matrix 
        arr_points (array - nx2 array with x and y values (units of pixels) of the points in the dicom image plane for conversion
        
    Returns:
        list of lists - 1 x n x 3
    """
    # conversion as described in https://dicom.innolitics.com/ciods/rt-dose/roi-contour/30060039/30060040/30060050
    # modified for inversion purpose: P = Mx + S / x = M^-1(P-S)
    matrix = np.zeros((3, 3))
    # read in relevant dicom tags
    image_position   = np.asarray(dcm[0x0020, 0x0032].value, np.double)
    direction_cosine = np.asarray(dcm[0x0020, 0x0037].value, np.double)
    pixel_spacing    = np.asarray(dcm[0x0028, 0x0030].value, np.double)
    # create the matrix
    matrix[:3,0] = direction_cosine[:3]
    matrix[:3,1] = direction_cosine[3:6]
    orthogonal   = np.cross(direction_cosine[0:3], direction_cosine[3:])
    matrix[:3,2] = orthogonal / np.linalg.norm(orthogonal)
    # ics -> rcs
    vector = np.zeros((arr_points.shape[0], 3))
    vector[:, 1] = arr_points[:, 0] * pixel_spacing[0]
    vector[:, 0] = arr_points[:, 1] * pixel_spacing[1]
    product = np.transpose(np.dot(matrix, np.transpose(vector))) # x y z 1
    product = np.add(product[:, 0:3], image_position.reshape((1, 3)))
    return product


def sort_dcms(dcms):
    # attempt at sorting
    try:
        sortable = sorted([[dcm, dcm.SliceLocation] for dcm in dcms], key=lambda x: x[1])
        dcms = [a[0] for a in sortable]
    except: pass
    try:
        sortable = sorted([[dcm, dcm.InstanceNumber] for dcm in dcms], key=lambda x: x[1])
        dcms = [a[0] for a in sortable]
    except: pass
    try:
        sortable = sorted([[dcm, dcm.SliceLocation, dcm.InstanceNumber] for dcm in dcms], key=lambda x: (x[1],x[2]))
        dcms = [a[0] for a in sortable]
    except: pass
    return dcms



############################
## PYQT5 Helper Functions ##
############################

def findMainWindow():
    # Global function to find the (open) QMainWindow in application
    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow) and not isinstance(widget, mpl_backend.MainWindow): 
            return widget
    return None


def findCCsOverviewTab():
    try: from Lumos.Guis.Comparison_Tabs.CCs_Overview_Tab import CCs_Overview_Tab
    except Exception as e: print(e); return None
    mainWin = findMainWindow()
    databasetab = mainWin.tab
    tabs = databasetab.tabs
    for i in range(tabs.count()):
        tab = tabs.widget(i)
        if isinstance(tab, CCs_Overview_Tab): return tab

