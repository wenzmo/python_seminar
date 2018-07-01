# ############################################################################################################# #
# (c) Moritz Wenzler, Humboldt-Universität zu Berlin, 4/24/2018
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import seaborn as sns
import sklearn # scikit-learn in library
import os
import gdal
import ogr
import osr
import numpy as np
from sklearn.model_selection import train_test_split
import struct

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
indir = "/home/mo/Dokumente/python_seminar/Session_10/indata/raster/"
indir_shape = "/home/mo/Dokumente/python_seminar/Session_10/indata/"
outdir = "/home/mo/Dokumente/python_seminar/Session_10/outdata/"

# ####################################### FUNCTIONS ########################################################## #

def TransformGeometry(geometry, target_sref):
    '''Returns cloned geometry, which is transformed to target spatial reference'''
    geom_sref= geometry.GetSpatialReference()
    transform = osr.CoordinateTransformation(geom_sref, target_sref)
    geom_trans = geometry.Clone()
    geom_trans.Transform(transform)
    return geom_trans

def SpatialReferenceFromRaster(ds):
    '''Returns SpatialReference from raster dataset'''
    pr = ds.GetProjection()
    sr = osr.SpatialReference()
    sr.ImportFromWkt(pr)
    return sr

def PointToRast(point,gt):
    x, y = point.GetX(), point.GetY()
    px = int((x - gt[0]) / gt[1])
    py = int((y - gt[3]) / gt[5])
    return(px, py)


def corner_function(x):
    #create empty result list


    # empty lists for each coordinate part
    ulx_all = []
    uly_all = []
    lrx_all = []
    lry_all = []

    for ras in x:
        # get raster
        src = gdal.Open(indir + ras)
        # get upper left x and upper left y plus resolutions
        # ulx, uly is the upper left corner, lrx, lry is the lower right corner
        ulx, xres, xskew, uly, yskew, yres  = src.GetGeoTransform()
        # calculate lower right x and lower right y
        lrx = ulx + (src.RasterXSize * xres)
        lry = uly + (src.RasterYSize * yres)
        # add each coordinate to the corresponding lists
        ulx_all.append(ulx)
        uly_all.append(uly)
        lrx_all.append(lrx)
        lry_all.append(lry)
        # add the coordinates to the corner list, in which the four coordinates are stored for each raster
        corner_list.append((ras,ulx,uly,lrx,lry))
    # add the result coordinates to the result list
    result_list.append(("lower left x=",max(ulx_all),"y=",max(lry_all)))
    result_list.append(("upper left x=",max(ulx_all),"y=",min(uly_all)))
    result_list.append(("lower right x=", min(lrx_all), "y=", max(lry_all)))
    result_list.append(("upper right x=", min(lrx_all), "y=", min(uly_all)))
    # print the result
    print("coordinates of bounding box")
    for p in result_list:
        print(p)
    return result_list
    return corner_list


# ####################################### PROCESSING ########################################################## #
driver = ogr.GetDriverByName('ESRI Shapefile')
points = driver.Open(indir_shape + "RandomPoints.shp")
points_lyr = points.GetLayer()

raster_list = os.listdir(indir)
result_list = []
# just a list in which all corner coordinates are stored
corner_list = []

# run function
corner_function(raster_list)


ras1 = gdal.Open(indir + "LE07_L1TP_117056_20040211_20170122_01_T1_sr_evi.tif")
ras1_b = ras1.GetRasterBand(1)
ras2 = gdal.Open(indir + "LE07_L1TP_117056_20130627_20161124_01_T1_sr_evi.tif")
ras2_b = ras2.GetRasterBand(1)
ras3 = gdal.Open(indir + "LT05_L1TP_117056_19980407_20161228_01_T1_sr_evi.tif")
ras3_b = ras3.GetRasterBand(1)
ras4 = gdal.Open(indir + "LT05_L1TP_117056_20000717_20161214_01_T1_sr_evi.tif")
ras4_b = ras4.GetRasterBand(1)

sr_ras1 = SpatialReferenceFromRaster(ras1)
sr_ras2 = SpatialReferenceFromRaster(ras2)
sr_ras3 = SpatialReferenceFromRaster(ras3)
sr_ras4 = SpatialReferenceFromRaster(ras4)

sr_all = [sr_ras1,sr_ras2,sr_ras3,sr_ras4]

gt_r1 = ras1.GetGeoTransform()
inv_gt_r1 = gdal.InvGeoTransform(gt_r1)
gt_r2 = ras2.GetGeoTransform()
inv_gt_r2 = gdal.InvGeoTransform(gt_r2)
gt_r3 = ras3.GetGeoTransform()
inv_gt_r3 = gdal.InvGeoTransform(gt_r3)
gt_r4 = ras4.GetGeoTransform()
inv_gt_r4 = gdal.InvGeoTransform(gt_r4)

# classification array

inv_gt_all = [inv_gt_r1,inv_gt_r2,inv_gt_r3,inv_gt_r4]

res_all = gt_r1[1]


cols_all = round(int(result_list[3][1]-result_list[1][1])/res_all)
#cols_all
rows_all = round(int(result_list[1][3]-result_list[0][3])/res_all)
#rows_all


difx_r1 = round(int(result_list[1][1] - corner_list[2][1])/res_all)
dify_r1 = round(int(corner_list[2][2] - result_list[1][3])/res_all)

difx_r2 = round(int(result_list[1][1] - corner_list[1][1])/res_all)
dify_r2 = round(int(corner_list[1][2] - result_list[1][3])/res_all)

difx_r3 = round(int(result_list[1][1] - corner_list[3][1])/res_all)
dify_r3 = round(int(corner_list[3][2] - result_list[1][3])/res_all)

difx_r4 = round(int(result_list[1][1] - corner_list[0][1])/res_all)
dify_r4 = round(int(corner_list[0][2] - result_list[1][3])/res_all)

arr_r1 = ras1_b.ReadAsArray(difx_r1,dify_r1,cols_all, rows_all).astype(np.int16)
arr_r2 = ras2_b.ReadAsArray(difx_r2,dify_r2,cols_all, rows_all).astype(np.int16)
arr_r3 = ras3_b.ReadAsArray(difx_r3,dify_r3,cols_all, rows_all).astype(np.int16)
arr_r4 = ras4_b.ReadAsArray(difx_r4,dify_r4,cols_all, rows_all).astype(np.int16)

xdim_arr1 = np.size(arr_r1,0)
ydim_arr1 = np.size(arr_r1,1)

out_array_class = np.zeros(((xdim_arr1 * ydim_arr1) , 4), dtype=np.int16)

arr_all = [arr_r1, arr_r2, arr_r3, arr_r4]
for i in range(len(arr_all)):
    out_array_class[:,i] = arr_all[i].ravel() # ravel() reduces the dimensions of an array
out_array_class

# trainingsdata array

out_array_train = np.zeros((len(points_lyr) , 4), dtype=np.int16)
out_array_feat = np.zeros((len(points_lyr) , 1), dtype=np.int16)

feat = points_lyr.GetNextFeature()

counter = int(0)

while feat:
    for iter in range(0, len(inv_gt_all), 1):
        geom = feat.GetGeometryRef()
        geom_cp = geom.Clone()
        name_geom = feat.GetField("Class")

        #print(feat.GetField("ID")); print(feat.GetField("Class"))


        point = TransformGeometry(geom_cp, sr_all[iter])
        # print(point_r1.GetSpatialReference())
        # get coordinates
        env = point.GetEnvelope()
        # check if ppoints are within corners
        rules = [env[0] >= result_list[0][1],
                 env[0] <= result_list[3][1],
                 env[2] >= result_list[0][3],
                 env[2] <= result_list[3][3]]
        #print(rules)
        if all(rules):
            #print(counter,"all in bounds")
            offsets = gdal.ApplyGeoTransform(inv_gt_all[iter], env[0], env[2])
            xoff, yoff = map(int, offsets)
            value = ras1_b.ReadAsArray(xoff, yoff, 1, 1)[0, 0]

            out_array_train[counter][iter] = value
            out_array_feat[counter][0] = name_geom

        else: # if not in corners set na values (9999)
            out_array_train[counter][iter] = 9999
            out_array_feat[counter][0] = 9999
    counter = counter + int(1)
    geom = None
    feat = points_lyr.GetNextFeature()
points_lyr.ResetReading()

# romve na values (9999)
out_array_train_nan = (out_array_train == 9999).sum(1)
out_array_train_no_nan = out_array_train[out_array_train_nan == 0, :]

out_array_feat_nan = (out_array_feat == 9999).sum(1)
out_array_feat_no_nan = out_array_feat[out_array_feat_nan == 0, :]

# get x and x dim
xdim_class = np.size(out_array_class,0)
ydim_class = np.size(out_array_class,1)

xdim_train = np.size(out_array_train_no_nan,0)
ydim_train = np.size(out_array_train_no_nan,1)

xdim_feat = np.size(out_array_feat_no_nan,0)
ydim_feat = np.size(out_array_feat_no_nan,1)

# write as .npy
outName_lab = str(str(outdir) + "trainingDS_labels_" + str(xdim_train) + "_" + str(ydim_train) + ".npy")
np.save(outName_lab, out_array_train_no_nan)

outName_feat = str(str(outdir) + "trainingDS_features_" + str(xdim_feat) + "_" + str(ydim_feat) + ".npy")
np.save(outName_feat, out_array_feat_no_nan)

outName_class = str(str(outdir) + "trainingDS_labels_" + str(xdim_class) + "_" + str(ydim_class) + ".npy")
np.save(outName_class, out_array_class)











# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")