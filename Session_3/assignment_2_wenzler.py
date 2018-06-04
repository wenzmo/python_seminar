# ############################################################################################################# #
# (c) Moritz Wenzler, Humboldt-Universität zu Berlin, 4/24/2018
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
import os
from osgeo import gdal

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #

dir_p1 = "/home/mo/Dokumente/Python_course/Session_3/Week04_Assignment/"
Out_path = "/home/mo/Dokumente/Python_course/Session_3/"

# ####################################### PROCESSING ########################################################## #

# get raster names
raster_list = os.listdir(dir_p1)

def corner_function(x):
    #create empty result list
    result_list = []
    # just a list in which all corner coordinates are stored
    corner_list = []
    # empty lists for each coordinate part
    ulx_all = []
    uly_all = []
    lrx_all = []
    lry_all = []

    for ras in x:
        # get raster
        src = gdal.Open(dir_p1 + ras)
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
        corner_list.append((ulx,uly,lrx,lry))
    # add the result coordinates to the result list
    result_list.append(("lower left x=",max(ulx_all),"y=",max(lry_all)))
    result_list.append(("upper left x=",max(ulx_all),"y=",min(uly_all)))
    result_list.append(("lower right x=", min(lrx_all), "y=", max(lry_all)))
    result_list.append(("upper right x=", min(lrx_all), "y=", min(uly_all)))
    # print the result
    print("coordinates of bounding box")
    for p in result_list:
        print(p)

# run function
corner_function(raster_list)



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")