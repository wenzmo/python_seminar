# ############################################################################################################# #
# (c) Moritz Wenzler, Humboldt-Universität zu Berlin, 4/24/2018
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import ogr, osr
import os
import pandas as pd
import gdal
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
os.chdir("/home/mo/Dokumente/python_seminar/Session_9/indata")
# ####################################### Functions ########################################################## #
def TransformGeometry(geometry, target_sref):
    '''Returns cloned geometry, which is transformed to target spatial reference'''
    geom_sref = geometry.GetSpatialReference()
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
# ####################################### PROCESSING ########################################################## #

parcels = ogr.Open("Parcels.shp")
parcels_lyr = parcels.GetLayer()
parcels_cs = parcels_lyr.GetSpatialRef()

roads = ogr.Open("Roads.shp")
roads_lyr = roads.GetLayer()

thp = ogr.Open("TimberHarvestPlan.shp")
thp_lyr = thp.GetLayer()

# Get Projection infos
mary = ogr.Open("Marihuana_Grows.shp")
mary_lyr = mary.GetLayer()
mary_cs = mary_lyr.GetSpatialRef()

dem = gdal.Open("DEM_Humboldt.tif")

i = 0
id = 0

out_df = pd.DataFrame(columns=["Parcel APN", "NR_GH-Plants", "NR_OD-Plants", "Dist_to_grow_m", "Km Priv. Road", "Km Local Road", "Mean elevation", "PublicLand_YN", "Prop_in_THP"])

feat = parcels_lyr.GetNextFeature()
while feat:
    geom = feat.GetGeometryRef()
    apn = feat.GetField('APN')
    #
    # ############################################################# #
    #### Group 1 #####
    geom_par = feat.geometry().Clone()
    geom_par.Transform(osr.CoordinateTransformation(parcels_cs, mary_cs))

    mary_lyr.SetSpatialFilter(geom_par)

    total_gh = total_od = 0

    point_feat = mary_lyr.GetNextFeature()
    while point_feat:
        total_gh += point_feat.GetField('g_plants')
        total_od += point_feat.GetField('o_plants')
        point_feat = mary_lyr.GetNextFeature()
    mary_lyr.ResetReading()
    #print(total_od,total_gh)

    #### Group 2 #####

    id += 1
    parcel = geom_par.Clone()
    distance = []
    mary_lyr.SetSpatialFilter(parcel)
    feature_count = mary_lyr.GetFeatureCount()
    print("ID: " + str(id) + " Feature Count: " + str(feature_count))
    if feature_count > 0:
        mary_lyr.SetSpatialFilter(None)
        bufferSize = 0
        exit = 0
        while exit == 0:
            bufferSize = bufferSize + 10

            buffer = parcel.Buffer(bufferSize)
            mary_lyr.SetSpatialFilter(buffer)
            buffer_count = mary_lyr.GetFeatureCount()
            print("Current buffer size: " + str(bufferSize) + "Current buffer count:" + str(buffer_count))
            # check if more marijuana plants in the buffer as in the parcel
            if buffer_count > feature_count:
                exit += 1
                distance.append = bufferSize
        mary_lyr.SetSpatialFilter(None)

    ######### Group 3 ############

    # Set filter for relevant road types
    roads_lyr.SetAttributeFilter("FUNCTIONAL IN ('Local Roads', 'Private')")
    # loop through two categories
    road_feat = roads_lyr.GetNextFeature()
    while road_feat:
        functional = road_feat.GetField('FUNCTIONAL')
        geom_roads = road_feat.GetGeometryRef()
        intersection = geom.Intersection(geom_roads)        # calculate intersection of road types and individual parcel
        length = intersection.Length()                      # get length of intersection
        #print(functional, length)
        if functional == 'Local Roads':
            len_loc = length
        else:
            len_loc = 0
        if functional == 'Private':
            len_priv = length
        else:
            len_priv = length
        road_feat = roads_lyr.GetNextFeature()

    area_parcel = geom.GetArea()

    # timber harvest plan > only use one year (overlapping geometries)
    thp_lyr.SetAttributeFilter("THP_YEAR = '1999'")
    thp_lyr.SetSpatialFilter(geom)                  # Set filter for parcel
    thp_feat = thp_lyr.GetNextFeature()
    area_parcel = geom.GetArea()                    # area of parcel
    thp_list = []

    # loop through selected features
    while thp_feat:
        geom_thp = thp_feat.GetGeometryRef()
        intersect_thp = geom.Intersection(geom_thp) # intersection of parcel and selected thp features
        area = intersect_thp.GetArea()              # area of intersected thp feature
        thp_list.append(area)                       # add area of thp feature to list
        thp_feat = thp_lyr.GetNextFeature()

    thp_sum = sum(thp_list)                         # sum up all thp features in parcel
    thp_prop = thp_sum/area_parcel
    print(thp_prop)

    ##### group 4 #####


    # read raster


    drv = ogr.GetDriverByName('ESRI Shapefile')

    p_geom = TransformGeometry(geom_par, SpatialReferenceFromRaster(dem))

    # feat_env = p_geom.GetEnvelope()
    x_min, x_max, y_min, y_max = p_geom.GetEnvelope()

    drv_mem = ogr.GetDriverByName("Memory")
    ds = drv_mem.CreateDataSource("")
    ds_lyr = ds.CreateLayer("", SpatialReferenceFromRaster(dem), ogr.wkbPolygon)
    featureDefn = ds_lyr.GetLayerDefn()
    out_feat = ogr.Feature(featureDefn)
    out_feat.SetGeometry(p_geom)
    ds_lyr.CreateFeature(out_feat)
    out_feat = None

    # Create the destination data source
    gt = dem.GetGeoTransform()
    pr = dem.GetProjection()
    NoData_value = 0

    x_res = int((x_max - x_min) / gt[1])
    y_res = int((y_max - y_min) / gt[1])
    target_ds = gdal.GetDriverByName('GTiff').Create('test2.tif', x_res, y_res, gdal.GDT_Byte)
    target_ds.SetGeoTransform((x_min, x_res, 0, y_max, 0, y_res))
    target_ds.SetProjection(pr)
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)

    gdal.RasterizeLayer(target_ds, [1], ds_lyr, burn_values=[1])


    target_array = target_ds.ReadAsArray()
    target_ds = None


    # ############################################################# #
    #


    out_df.loc[len(out_df) + 1] = [apn, total_gh, total_od, distance,length[1],length[0],mean_elev,thp_prop,thp_sum]  # insert further variables from other groups

    feat = parcels_lyr.GetNextFeature()

parcels_lyr.ResetReading()

out_df.to_csv("output_humboldt_county.csv", index=None, sep=',', mode='a')



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")