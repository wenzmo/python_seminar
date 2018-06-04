# ############################################################################################################# #
#
# (c) Moritz Wenzler, Humboldt-Universität zu Berlin, 4/24/2018
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import os
import pandas as pd
import numpy as np
from collections import Counter
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
dir_p1 = "/home/mo/Dokumente/Python_course/Session_2/Assignment01_data/Part01_Landsat/"
dir_p2 = "/home/mo/Dokumente/Python_course/Session_2/Assignment01_data/Part02_GIS-Files/"
Out_path = "/home/mo/Dokumente/Python_course/Session_2/"


# ####################################### PROCESSING ########################################################## #

# ######### question 1 ##########

landsat = os.listdir(dir_p1)  # get all files' and folders' names in the current directory


# get files
result = []
for filename in landsat:
    new = os.listdir(os.path.join(dir_p1,filename))
    result.append(new)

sens_list = []
for a in result:
    for b in a:
        sens_list.append(b[0:4])

# intilize a null list
landsat_sens = []

# traverse for all elements
for x in sens_list:
    # check if exists in unique_list or not
    if x not in landsat_sens:
        landsat_sens.append(x)
            # print list


# split into different scenes and count per sensors
result2 = []
for foot in result:
    # convert list in strings
    temp1 = str(foot)
    for sens in landsat_sens:
        # count each sensor per footprint
        temp2 = temp1.count(sens)
        # add counts for sensor to result list
        result2.append(str(sens + " = " + str(temp2)))
        # add name footprint to results
    result2.append(str(temp1[6:12]))
print(result2)

# split into footprints
composite_list = [result2[x:x+5] for x in range(0, len(result2),5)]
#print(composite_list)

# show results (just for a better view)
for show in composite_list:
    print(show)


# ########### question 2 and 3 #############

df = pd.DataFrame()
df_all = pd.DataFrame()

for foldername in landsat:
    # get all foldernames of the scenes
    new2_1 = os.listdir(os.path.join(dir_p1,foldername))
    for filename in new2_1:
        # get complete path of the folders, for later use, create this variable
        path_new = os.path.join(dir_p1, foldername, filename)
        # get all data in the scenesfolder
        files = os.listdir(path_new)
        # get name of sensor
        sensor = filename[:4]
        # get number of files of the folder
        size = len(files)
        # create dataframe with sesnor, size and path information
        df_new = pd.DataFrame(data={'sensor': [sensor], 'size': [size], "path": [path_new]})
        # add to sub result dataframe
        df = df.append(df_new)
    # add to final dataframe
    df_all = df_all.append(df)


false_columns = pd.DataFrame()
df_false = pd.DataFrame()
for sens in landsat_sens:
    # get all rows from each sensor
    df_sens = df_all.loc[(df_all['sensor'] == sens)]
    # get mode from sensor size
    mode_sens = df_sens.mode(numeric_only = True)
    # if there are values different from mode wirte these rows to a new dataframe
    if (len(df_sens[df_sens["size"] != int(mode_sens.iloc[0])]) > 0):
        df_false = df_false.append(df_sens.loc[(df_sens["size"] != int(mode_sens.iloc[0]))])

# get only the path
df_false_paths = df_false["path"]

# get number of corrupted folders
print("number of corrupted scenes =", len(df_false_paths))

# write the txt file
df_false_paths.to_csv(Out_path + str("corrupted scnenes wenzler.txt"), header=None, index=None, sep=' ', mode='a')


# ########### question 4 #############

# get files
files_p2 = os.listdir(dir_p2)  # get all files' and folders' names in the current directory

files_p2_df = pd.DataFrame()
for data in files_p2:
    # convert data in string
    data = str(data)
    # create dataframe with name of data
    df_p2 = pd.DataFrame(data={'data': [data]})
    # aks if the endeing of the name is .shp
    if data.endswith((".shp")):
        df_ends = pd.DataFrame(data={"ends": [str("shp")]}) # if true write shp
    # aks if the endeing of the name is .tif
    elif data.endswith((".tif")):
        df_ends = pd.DataFrame(data={"ends": [str("tif")]}) # if true write tif
    else:
        df_ends = pd.DataFrame(data={"ends": [str("none")]}) # if false write none
    # combine both dataframes
    data_comb = pd.concat([df_p2, df_ends], axis=1, join='inner')
    # add dataframe to result dataframe
    files_p2_df = files_p2_df.append(data_comb)

# count number of data that ends on shp
count_shp = len(files_p2_df[files_p2_df["ends"] == "shp"])
print("number of shapefiles =", count_shp)
# count number of data that ends on tif
count_tif = len(files_p2_df[files_p2_df["ends"] == "tif"])
print("number of tifs = ", count_tif)


# ########### question 5 and 6 #############

df_q5 = pd.DataFrame()
df_q5_all = pd.DataFrame()


for filename in files_p2:
    # split data in names and endings
    name = filename.split(".")
    # create dataframe with sesnor, size and path information
    df_new = pd.DataFrame(data={'name': [name[0]], 'ending': [name[-1]]})
    # add to final dataframe
    df_q5_all = df_q5_all.append(df_new)



#### shapefiles #####

# get all rows with ending shp
df_shp = pd.DataFrame()
df_shp = df_shp.append(df_q5_all.loc[df_q5_all["ending"] == "shp"])

# get all shp
df_shp_all = pd.DataFrame()
for shp in df_shp["name"]:
    df_shp_all = df_shp_all.append(df_q5_all.loc[df_q5_all["name"] == shp])

# get unique names for shp
df_unique_shp = []

for x in df_shp_all["name"]:
    # check if exists in unique_list or not
    if x not in df_unique_shp:
        df_unique_shp.append(x)
            # print list


cor_df_shp = pd.DataFrame()
# endings that are needed
endings_shp = ('shp', 'shx', 'dbf', 'prj')

for uniname in df_unique_shp:
    # get rows with specific names
    df_name = df_q5_all.loc[(df_q5_all['name'] == uniname)]
    # ask if there are all endings in there
    if (len(df_name.loc[df_name["ending"].isin(endings_shp)]) < 4):
        # create new dataframe if there are corrupted shapefiles
        df_cor = pd.DataFrame(data={"name": [str(uniname)]})
        # get the name of the corrupted shp
        cor_df_shp = cor_df_shp.append(df_cor[0:1])

# print how many shp are corrupted
print("number of corrupted shapefiles =",len(cor_df_shp))

# write the txt file
cor_df_shp.to_csv(Out_path + str("corrupted shapefiles wenzler.txt"), header=None, index=None, sep=' ', mode='a')



# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")