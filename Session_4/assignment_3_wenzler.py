# ############################################################################################################# #
# (c) Moritz Wenzler, Humboldt-Universität zu Berlin, 4/24/2018
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import gdal
import os
import numpy as np
import pandas as pd


# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
indir = "/home/mo/Dokumente/Python_course/Session_4/raster/"
outdir = "/home/mo/Dokumente/Python_course/Session_4/"
# ####################################### PROCESSING ########################################################## #

ras_slope = gdal.Open(indir + "SLOPE_Humboldt_sub.tif")
ras_dem = gdal.Open(indir + "DEM_Humboldt_sub.tif")
ras_thp = gdal.Open(indir + "THP_Humboldt_sub.tif")

### get the basic properties of the raster file
## slope
gt_sl = ras_slope.GetGeoTransform()
pr_sl = ras_slope.GetProjection()
cols_sl = ras_slope.RasterXSize
rows_sl = ras_slope.RasterYSize
nbands_sl = ras_slope.RasterCount

### Get the raster values (from the entire raster)
rb_sl = ras_slope.GetRasterBand(1)
dtype_sl = rb_sl.DataType
arr_sl = rb_sl.ReadAsArray(0,0,cols_sl, rows_sl)

## dem
gt_dem = ras_dem.GetGeoTransform()
pr_dem = ras_dem.GetProjection()
cols_dem = ras_dem.RasterXSize
rows_dem = ras_dem.RasterYSize
nbands_dem = ras_dem.RasterCount

### Get the raster values (from the entire raster)
rb_dem = ras_dem.GetRasterBand(1)
dtype_dem = rb_dem.DataType
arr_dem = rb_dem.ReadAsArray(0,0,cols_dem, rows_dem)

## thp
gt_thp = ras_thp.GetGeoTransform()
pr_thp = ras_thp.GetProjection()
cols_thp = ras_thp.RasterXSize
rows_thp = ras_thp.RasterYSize
nbands_thp = ras_thp.RasterCount

### Get the raster values (from the entire raster)
rb_thp = ras_thp.GetRasterBand(1)
dtype_thp = rb_thp.DataType
arr_thp = rb_thp.ReadAsArray(0,0,cols_thp, rows_thp)

## resolution of all rastera
res_all = gt_sl[1]


#### get extent and resolution of slope, dem and thp ####
raster_list = os.listdir(indir)
result_list = []
# just a list in which all corner coordinates are stored
corner_list = []
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
# run function
corner_function(raster_list)

## create arrays by new extent

cols_all = round(int(result_list[3][1]-result_list[1][1])/res_all)
#cols_all
rows_all = round(int(result_list[1][3]-result_list[0][3])/res_all)
#rows_all

# dif upperleft of slope and all
# get xoff
# slope
difx_sl = round(int(result_list[1][1] - corner_list[0][1])/res_all)
dify_sl = round(int(corner_list[0][2] - result_list[1][3])/res_all)
# dem
difx_dem = round(int(result_list[1][1] - corner_list[1][1])/res_all)
dify_dem = round(int(corner_list[1][2] - result_list[1][3])/res_all)
#thp
difx_thp = round(int(result_list[1][1] - corner_list[2][1])/res_all)
dify_thp = round(int(corner_list[2][2] - result_list[1][3])/res_all)

arr_sl = rb_sl.ReadAsArray(difx_sl,dify_sl,cols_all, rows_all).astype(float)
arr_dem = rb_dem.ReadAsArray(difx_dem,dify_dem,cols_all, rows_all).astype(float)
arr_thp = rb_thp.ReadAsArray(difx_thp,dify_thp,cols_all, rows_all).astype(float)

## check which are uncommen (or NA) values
np.unique(arr_sl)
np.unique(arr_dem)
np.unique(arr_thp)

# replace na values with 0
arr_sl[arr_sl < int(0)] = np.nan # here negeative values as nas
arr_dem[arr_dem == int(65536)] = np.nan # here 65535 as nas
arr_thp[arr_thp == int(65535)] = np.nan

print("mean slope" ,round(np.nanmean(arr_sl),2))
print("max slope" ,round(np.nanmax(arr_sl),2))
print("min slope" ,round(np.nanmin(arr_sl),2))
print("mean dem" ,round(np.nanmean(arr_dem),2))
print("max dem" ,round(np.nanmax(arr_dem),2))
print("min dem" ,round(np.nanmin(arr_dem),2))

# task 2
# binary raster where elevatoin < 1000m and slope < 30deg
# slope < 30 deg

arr_sl_bin = np.nan_to_num(arr_sl)
arr_sl_bin[arr_sl_bin < float(30.00)] = 1
arr_sl_bin[arr_sl_bin >= float(30.00)] = 0

np.unique(arr_sl_bin)

# elevation < 1000m
arr_dem_bin = np.nan_to_num(arr_dem)
arr_dem_bin[arr_dem_bin < float(1000.00)] = 1
arr_dem_bin[arr_dem_bin >= float(1000.00)] = 0


np.unique(arr_dem_bin)

# combine the two arrays
arr_comb = arr_dem_bin + arr_sl_bin

np.unique(arr_comb)


# if value 2, both alyers have 1, else write a 0
arr_comb[arr_comb <= int(1)] = 0
arr_comb[arr_comb == int(2)] = 1

np.unique(arr_comb)

print("proportion of ones",round((np.count_nonzero(arr_comb == 1)/np.count_nonzero(arr_comb >= 0))*100,2),"%")

# write array as raster


# (array, offset_x, offset_y

## task 2

# calculate for each year mean slope and mean elev
outfile = outdir + "binary_dem_slope.tif"
# 1. Create a driver with which we write the output
drvR = gdal.GetDriverByName('GTiff')
# 2. Create the file (here: allthough exactly the same, we go through the syntax)
dtype = ras_slope.GetRasterBand(1).DataType
nbands = ras_slope.RasterCount
outDS = drvR.Create(outfile, cols_all, rows_all, nbands, dtype)
pr = pr_thp
outDS.SetProjection(pr)
gt = [result_list[1][1],res_all,float(0.0),result_list[1][3],float(0.0),-res_all]
outDS.SetGeoTransform(gt)
# 3. Write the array into the newly generated file
outDS.GetRasterBand(1).WriteArray(arr_comb)
outDS = None
#out_band.FlushCache()
#out_band.ComputeStatistics(True)

# gte unique years
thp_uni = np.unique(arr_thp)
thp_uni = thp_uni[~np.isnan(thp_uni)]

result_thp = []
for years in thp_uni:
    mean_sl = round(np.nanmean(arr_sl[arr_thp == years]))
    mean_elev = round(np.nanmean(arr_dem[arr_thp == years]))
    result_thp.append([years, mean_elev, mean_sl])

# create a dataframe from the list to export it as csv
result_thp_df = pd.DataFrame(result_thp, columns = ["Year", "Mean_elev", "Mean_slope"])

result_thp_df.to_csv(outdir + str("results_thp_elev_slope_wenzler.csv"),
                     header= True, index=None, sep=',', mode='a',
                        float_format = '%.2f')


# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")