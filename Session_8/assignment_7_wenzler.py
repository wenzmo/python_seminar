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
out_ref_e = osr.SpatialReference()
out_ref_e.ImportFromWkt(proj_e)

proj_d = dist.GetProjection()
out_ref_d = osr.SpatialReference()
out_ref_d.ImportFromWkt(proj_d)


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

def point_to_rast(point,gt):
    x, y = point.GetX(), point.GetY()
    px = int((x - gt[0]) / gt[1])
    py = int((y - gt[3]) / gt[5])
    return(px, py)

while feature:
    geom = feature.GetGeometryRef()

    point_old = reproject_point(geom, old_lyr.GetSpatialRef())
    point_priv = reproject_point(geom, priv_lyr.GetSpatialRef())
    point_e = reproject_point(geom, out_ref_e)
    #print(point_e.GetSpatialReference())

    px_e, py_e = point_to_rast(point_e,gt_elev)

    point_d = reproject_point(geom, out_ref_d)
    #print(point_d.GetSpatialReference())

    px_d, py_d = point_to_rast(point_d,gt_dist)


    old_lyr.SetSpatialFilter(point_old)

    if old_lyr.GetFeatureCount() > 0:
        old_bin = int(1)

    priv_lyr.SetSpatialFilter(point_priv)

    if priv_lyr.GetFeatureCount() > 0:
        priv_bin = int(1)

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