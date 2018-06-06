# ############################################################################################################# #
# (c) Moritz Wenzler, Humboldt-Universität zu Berlin, 4/24/2018
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import numpy as np
#import ogr
#import pandas as pd
import gdal
import os




# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #

indir= "/home/mo/Dokumente/python_seminar/Session_7/data/"
outdir = "/home/mo/Dokumente/python_seminar/Session_7/out_data/"
# ####################################### PROCESSING ########################################################## #

raster = os.listdir(indir)
val = np.array([2, 3, 5, 11, 13, 18, 19, 1, 17])
size_rad = np.array([150, 300, 450])
iter = (0,1,2)

for ras in range(0, len(raster), 1):

    ras_sub = gdal.Open(indir + raster[ras])

    gt_sub= ras_sub.GetGeoTransform()
    #print(gt_sub[1],gt_sub[5])
    pr_sub = ras_sub.GetProjection()
    nbands_thp = ras_sub.RasterCount
    cols_sub = ras_sub.RasterXSize
    rows_sub = ras_sub.RasterYSize


    ### Get the raster values (from the entire raster)
    rb_sub = ras_sub.GetRasterBand(1)
    dtype_sub = rb_sub.DataType
    arr_sub = rb_sub.ReadAsArray(0, 0, cols_sub, rows_sub)


    for s in size_rad:
        bounds = int(s/gt_sub[1]-1)

        #sub = np.arange(25, dtype=np.float)
        #sub = np.reshape(sub,(5,5))
        #x =

        rcols = np.arange(0+bounds,cols_sub-bounds-1,1)
        rrows = np.arange(0+bounds,rows_sub-bounds-1,1)

        arr_sub_copy = np.arange(cols_sub*rows_sub, dtype=np.float)
        arr_sub_copy = np.reshape(arr_sub_copy,(cols_sub,rows_sub))
        arr_sub_copy[arr_sub_copy == arr_sub_copy] = 0.


        for ix in rrows:
            for iy in rcols:
                arr = arr_sub[ix-bounds:ix+bounds, iy-bounds:iy+bounds].copy()
                sdi_list = []
                for j in val:
                    size = arr.size
                    num = arr[arr == j].size
                    p = num/size
                    if p == 0:
                        sdi = 0
                    else:
                        sdi = -(p*np.log(p))
                    sdi_list.append(sdi)

                shdi = np.sum(sdi_list)

                arr_sub_copy[ix][iy] = float(shdi)

        # calculate for each year mean slope and mean elev
        outfile = outdir + str("ras_tile_") + str((ras+1)) + str("_window_size_") + str(s) + str(".tif")
        # 1. Create a driver with which we write the output
        drvR = gdal.GetDriverByName('GTiff')
        # 2. Create the file (here: allthough exactly the same, we go through the syntax)
        dtype = ras_sub.GetRasterBand(1).DataType
        nbands = ras_sub.RasterCount
        outDS = drvR.Create(outfile, cols_sub, rows_sub, nbands, dtype)
        outDS.SetProjection(pr_sub)
        outDS.SetGeoTransform(gt_sub)
        # 3. Write the array into the newly generated file
        outDS.GetRasterBand(1).WriteArray(arr_sub_copy)
        outDS = None
        #s = None





# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")