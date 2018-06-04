# ############################################################################################################# #
# (c) Moritz Wenzler, Humboldt-Universität zu Berlin, 4/24/2018
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import numpy as np
import ogr
import pandas as pd




# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
indir =  "/home/mo/Dokumente/Python_course/Session_5/"
outdir = "/home/mo/Dokumente/Python_course/Session_5/"
# ####################################### PROCESSING ########################################################## #


countries = ogr.Open("/home/mo/Dokumente/Python_course/Session_5/gadm36_dissolve.shp")
PA = ogr.Open("/home/mo/Dokumente/Python_course/Session_5/WDPA_May2018-shapefile-polygons.shp")
countrylayer = countries.GetLayer()
PAlayer = PA.GetLayer()

######### delete unnecessary data in PAlayer with attribute filter #########
PAlayer.SetAttributeFilter("MARINE='0'") # select PA on the land
PAlayer.SetAttributeFilter("STATUS='Designated' or STATUS='Established'") # select PA "Designated" or "Established"
PAlayer.SetAttributeFilter("IUCN_CAT='Ia' or IUCN_CAT='Ib' or IUCN_CAT='II' or IUCN_CAT='III' or IUCN_CAT='IV' or IUCN_CAT='V' or IUCN_CAT='VI'") # select PA belonging to Ia,Ib,...,VI

######### join countrylayer and PAlayer together with spatial filter, and select the columns we need into a new list #########
countryPA = []
for countryfeature in countrylayer: # a loop for all countries in countrylayer
    countryfeaturegeometry = countryfeature.geometry().Clone() # copy the geometry of a specific country
    PAlayer.SetSpatialFilter(countryfeaturegeometry) # apply spatial filter to PAlayer, so that we can select all PAs in this country
    for PAfeature in PAlayer: # a loop for all PAs in one specific country
        newfeature = []
        newfeature.append(str(countryfeature.GetField('ID_0')))
        newfeature.append(str(countryfeature.GetField('NAME_0')))
        newfeature.append(str(PAfeature.GetField('NAME')))
        newfeature.append(str(PAfeature.GetField('IUCN_CAT')))
        newfeature.append(str(PAfeature.GetField('STATUS_YR')))
        newfeature.append(str(PAfeature.GetField('GIS_AREA')))
        countryPA.append(newfeature)

######### change list to dataframe #########
columnsname1 = ['Country ID','Country Name','PA Name','IUCN_CAT','STATUS_YR','GIS_AREA'] # define the name of columns of the dataframe
df1 = pd.DataFrame(countryPA,columns=columnsname1) # this is a combined dataframe which contains information from both countrylayer and PAlayer
# df1.to_csv("O:/Student_Data/Mingjian/geoprocessing with python/process_table.csv",encoding='utf-8') # write dataframe to csv

######### carry out calculation with df1 and form the result dataframe we need #########
list_IUCN_CAT = ['Ia','Ib','II','III','IV','V','VI'] # create a list for all PA categories
country_category = []
j = 0
for j in range(0,len(df1)): # a loop for all countries
    country = []
    countryN = df1.loc[df1['Country ID'] == str(j)] # select PAs in one country
    if len(countryN) is 0: # if there is no PA in this country, go straight to the next country
        j = j+1
    else:
        country.append(countryN.iloc[0][0]) # country ID
        country.append(countryN.iloc[0][1]) # country Name
        country.append('ALL') # PA category
        country.append(len(countryN)) # #PAs
        areafloat1 = [float(i) for i in countryN['GIS_AREA']] # change str to float
        country.append(np.mean(areafloat1)) # mean area of PAs
        country.append(np.max(areafloat1)) # largest area of PAs
        PAareamax1 = countryN.loc[countryN['GIS_AREA'] == str(np.max(areafloat1))] # information of PA with largest area
        country.append(PAareamax1.iloc[0][2]) # name of largest PA
        country.append(PAareamax1.iloc[0][4]) # year of establish of largest PA
        country_category.append(country) # add data to result list
        n = 0
        for n in range(0,len(list_IUCN_CAT)): # a loop for all categories in a country (this loop is very similar to the former one)
            category = []
            categoryN = countryN.loc[countryN['IUCN_CAT'] == list_IUCN_CAT[n]]
            if len(categoryN) is 0:
                n=n+1
            else:
                category.append(categoryN.iloc[0][0])
                category.append(categoryN.iloc[0][1])
                category.append(categoryN.iloc[0][3])
                category.append(len(categoryN))
                areafloat2 = [float(i) for i in categoryN['GIS_AREA']]
                category.append(np.mean(areafloat2))
                category.append(np.max(areafloat2))
                PAareamax2 = categoryN.loc[categoryN['GIS_AREA'] == str(np.max(areafloat2))]
                category.append(PAareamax2.iloc[0][2])
                category.append(PAareamax2.iloc[0][4])
                country_category.append(category)
                n=n+1
        j = j+1

##### write df2 to result table #####
columnsname2 = ['Country ID','Country Name','PA Category','# PAs','Mean area of PAs','Area of largest PA','Name of largest PA','Year of establ. Of largest PA'] # define the name of columns of the dataframe
df2 = pd.DataFrame(country_category,columns=columnsname2)
df2.to_csv(outdir + "result_table.csv",encoding='utf-8')












# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")