# ############################################################################################################# #
# (c) Moritz Wenzler, Humboldt-Universität zu Berlin, 4/24/2018
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import osgeo.ogr, osgeo.osr
from osgeo import gdal, ogr, osr
from pyproj import Proj, transform
import geopandas as gpd
import pandas as pd
from math import modf
import random
import numpy as np
import os
import math
#import simplekml
from shapely.wkb import loads
from shapely import wkt

# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
indir= "/home/mo/Dokumente/python_seminar/Session_8/data/"
outdir = "/home/mo/Dokumente/python_seminar/Session_8/out_data/"
# ####################################### PROCESSING ########################################################## #

#1 load in data
driver = ogr.GetDriverByName("ESRI Shapefile")
old = driver.Open(indir + '/Old_Growth.shp')
priv = driver.Open(indir + '/PrivateLands.shp')
points = driver.Open(indir + '/Points.shp')
elev = gdal.Open(indir + '/Elevation.tif')
dist = gdal.Open(indir + '/DistToRoad.tif')

old_lyr = old.GetLayer()
print(old_lyr.GetSpatialRef())
priv_lyr = priv.GetLayer()
print(priv_lyr.GetSpatialRef())

proj_e = elev.GetProjection()
epsg_e = int(proj_e[199:203])
out_ref_e = osr.SpatialReference()
out_ref_e.ImportFromEPSG(epsg_e)

proj_d = dist.GetProjection()
l_p = len(proj_d)
epsg_d = int(proj_d[l_p-8:l_p-4])
out_ref_d = osr.SpatialReference()
out_ref_d.ImportFromEPSG(epsg_d)


#2 transform points into raster pixel
gt_elev = elev.GetGeoTransform()
gt_dist = dist.GetGeoTransform()

points_lyr = points.GetLayer()

feature = points_lyr.GetNextFeature()

def reproject_point(geom_point, out_ref):
    inSpatialRef = geom_point.GetSpatialReference()
    coordTrans = osr.CoordinateTransformation(inSpatialRef, out_ref)
    point_rep = ogr.CreateGeometryFromWkt("POINT (" + str(geom_point.GetX()) + " " + str(geom_point.GetY()) + ")")
    point_rep.Transform(coordTrans)
    return(point_rep)

while feature:
    geom = feature.GetGeometryRef()

    point_old = reproject_point(geom, old_lyr.GetSpatialRef())
    point_priv = reproject_point(geom, priv_lyr.GetSpatialRef())
    point_e = reproject_point(geom, out_ref_e)
    print(point_e.GetSpatialReference())
    mxe, mye = point_e.GetX(), point_e.GetY()

    px_e = int((mxe - gt_elev[0]) / gt_elev[1])
    py_e = int((mxe - gt_elev[3]) / gt_elev[5])
    px_e, py_e

    point_d = reproject_point(geom, out_ref_d)
    print(point_d.GetSpatialReference())
    mxd, myd = point_p.GetX(), point_p.GetY()

    px_p = int((mxp - gt_elev[0]) / gt_elev[1])
    py_p = int((myp - gt_elev[3]) / gt_elev[5])
    px_d, py_d

#3 get 1 or 0 if in shapes

#4 srite result in a table

# export table









# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")