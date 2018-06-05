
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
root_folder = "/home/mo/Dokumente/python_course/Session_6/"
# ####################################### PROCESSING ########################################################## #


#convert UTM to Lambert of PA shp file
tmp = gpd.GeoDataFrame.from_file(root_folder + '/WDPA_May2018_polygons_GER_select10large.shp')
tmpLambert = tmp.to_crs({'init':'EPSG:3035'})
tmpLambert.to_file(root_folder + 'WDPA_Lambert.shp')

#load shapefiles
driver = ogr.GetDriverByName("ESRI Shapefile")
CO_Germany = driver.Open(root_folder + '/gadm36_GERonly.shp')
PA_Germany = driver.Open(root_folder + '/WDPA_Lambert.shp')
Point = driver.Open(root_folder + '/OnePoint.shp')

CO_lyr = CO_Germany.GetLayer()
PA_lyr = PA_Germany.GetLayer()
Point_lyr = Point.GetLayer()
#print(PA_lyr.GetFeatureCount())

#convert UTM to Lambert of start point
inProj = Proj(init='epsg:32633')
outProj = Proj(init='epsg:3035')
outepsg = 3035
x1,y1 = 387989.426864,5819549.72673
x2,y2 = transform(inProj,outProj,x1,y1)
print(x2, y2)

# get crs
point_srs = ogr.osr.SpatialReference()
point_srs.ImportFromEPSG(3035)

# reate epmty dataframes
point_all_df = pd.DataFrame() # final list
point_df = pd.DataFrame() # pre result_list



#for pa_feat in PA_lyr:
#feature = PA_lyr.GetNextFeature()
for feature in PA_lyr:
#while feature:
     # ask if min 10 points are in list for this PA
        geom = feature.geometry().Clone()
        env = geom.GetEnvelope()#Get.Envelope returns minX, minY, maxX, maxY in env[0], env[2], env[1], env[3])
        name = feature.GetField('NAME')
        #print(name)
        #print("xmin:",env[0], "ymin:",env[2], "xmax:",env[1], "ymax:",env[3])

        xmin = env[0]
        xmax = env[1]
        ymin = env[2]
        ymax = env[3]

        PA_xmax = math.ceil(-((x2-xmax)/30))
        PA_xmin = math.ceil(-((x2-xmin)/30))
        PA_ymax = math.ceil(-((y2 - ymax) / 30))
        PA_ymin = math.ceil(-((y2 - ymin) / 30))

    while len(point_df) < 50:
        new_x = random.randrange(PA_xmin, PA_xmax, 30) # get a random x coordinate within the 30 meters interval
        new_y = random.randrange(PA_ymin, PA_ymax, 30) # same with y

        # create a geometry from coordinates
        pointCoord = (xmin + (new_x * 30)), (ymin + (new_y * 30))


        coord_df = pd.DataFrame(data={'x': [pointCoord[0]], 'y': [pointCoord[1]]})

        # create point geometry
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(pointCoord[0], pointCoord[1])



# aks if point is within the borders
        if geom.Contains(point):
            print("Point Within Borders ")
            # if true, aks if point is more than 60 meters away from border
            PA_wkt = wkt.loads(str(geom))
            point_wkt = wkt.loads(str(point))
            if PA_wkt.boundary.distance(point_wkt) >= 64: # point_geom.Distance(line_feat) >= 90
                print("Distnace to borders > 90m")
                print(pointCoord)
                point_df = point_df.append(coord_df)
                #if len(point_df) == 0:
                #    point_df = point_df.append(coord_df)
                #else:
                #    #if true, ask if one of the points from before is more then 90 meters away, to avoid overlapping polygons
                #    if (np.min(point_df["x"]) - 90) <= int(point_geom.GetX()) >= (np.min(point_df["x"]) + 90):
                #        print("TRUE")
                #        point_df = point_df.append(coord_df)
                #    else:
                #        print("FALSE")
                #        if (np.min(point_df["y"]) - 90) <= int(point_geom.GetY()) >= (np.min(point_df["y"]) + 90):
                #            print("TRUE")
                #            point_df = point_df.append(coord_df)
                #        else:
                #           print("FALSE")
            else:
                print("Point to close to borders")
        else:
            print("Point Not Within Borders")



        print(len(point_df))
    else:
        point_all_df = point_all_df.append(point_df)
        point_df = pd.DataFrame()
        #poly_feat = None
        #point_geom = None
        #feature = None     ##### crashes when i use this line and/or the next line
    #feature = PA_lyr.GetNextFeature()
PA_lyr.ResetReading()
len(point_all_df)/10



# get all coordinates from center coordinates

p10 = [point_all_df["x"].iloc[0],point_all_df["y"].iloc[0]]
p11 = [p10[0]-30, p10[1],]
p12 = [p10[0]-30, p10[1]+30,]
p13 = [p10[0], p10[1]+30,]
p14 = [p10[0]+30, p10[1]+30,]
p15 = [p10[0]+30, p10[1],]
p16 = [p10[0]+30, p10[1]-30,]
p17 = [p10[0], p10[1]-30,]
p18 = [p10[0]-30, p10[1]-30,]

p_cent_list = [p10,p11,p12,p13,p14,p15,p16,p17,p18]



### start with shapfile # this has to be in a loop form.....

fieldName_poly = 'ID'
fieldType_poly = ogr.OFTString
outSHPfn_poly = root_folder + 'poly1.shp'

# Create the output shapefile
shpDriver_poly = ogr.GetDriverByName("ESRI Shapefile")
if os.path.exists(outSHPfn_poly):
    shpDriver_poly.DeleteDataSource(outSHPfn_poly)
outDataSource_poly = shpDriver_poly.CreateDataSource(outSHPfn_poly)
outLayer_poly = outDataSource_poly.CreateLayer(outSHPfn_poly,
                                             point_srs,
                                             geom_type=ogr.wkbPolygon)

# create a field
idField_poly = ogr.FieldDefn(fieldName_poly, fieldType_poly)
outLayer_poly.CreateField(idField_poly)

# Create the feature and set values
featureDefn_poly = outLayer_poly.GetLayerDefn()
outFeature_poly = ogr.Feature(featureDefn_poly)

# kml
kml = simplekml.Kml(open=1)
pfol = kml.newfolder(name="poly_kml")


# create polygons from coordinates

for p_coords in p_cent_list:
    p10 = [p_coords[0],p_coords[1]]
    p10lo = [p10[0]-15, p10[1]+15,]
    p10ro = [p10[0]+15, p10[1]+15,]
    p10lu = [p10[0]-15, p10[1]-15,]
    p10ru = [p10[0]+15, p10[1]-15,]

    p_list = [p10lo,p10ro,p10ru,p10lu]
    ##### create polygons from points
    poly = ogr.Geometry(ogr.wkbPolygon)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for coord in p_list:
        x = coord[0]
        y = coord[1]
        print (x, y)
        ring.AddPoint(x,y)


    # Add first point again to ring to close polygon
    ring.AddPoint(p_list[0][0], p_list[0][1])

    # Add the ring to the polygon

    poly.AddGeometry(ring)
    ring = None
    p_list = None
    outFeature_poly.SetGeometry(poly)
    outFeature_poly.SetField(fieldName_poly, len(outLayer_poly) + 10) # 10 has to be replaced with the numbers of big 900x900 squares
    outLayer_poly.CreateFeature(outFeature_poly)
    poly = None


    i = 0
    for element in outLayer_poly:
        geom = loads(element.GetGeometryRef().ExportToWkb())
        i = i + 1
        arrcoords = geom.to_wkt()
        # this part is for the kml
        pol = pfol.newpolygon()
        pol.visibility = 0
        # 'trans Blue Poly'
        pol.style.polystyle.color = '7d00ff00'
        pol.altitudemode = 'relativeToGround'
        pol.extrude = 1
        # pol.outerboundaryis = ([(x1,y1),(x2,y2),(x3,y3),(x4,y4),(x1,y1)])
        coords = arrcoords.replace('POLYGON', '').replace('(', '').replace(')', '')
        coords = coords.replace('MULTI', '')
        coords = coords.split(',')
        asize = 1
        pol.outerboundaryis = (
        [(float(coords[j].split()[0]), float(coords[j].split()[1]), asize) for j in range(len(coords))])


# remove the inputs, to save the results

outFeature_poly = None
PA_Germany = None
outDataSource_poly = None

# save the kml
kml.save(root_folder + 'poly_kml')



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")