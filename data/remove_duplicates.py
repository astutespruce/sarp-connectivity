from pathlib import Path

import geopandas as gp

# Distance between points to consider as duplicates, in meters (CONUS Albers) projection.
TOLERANCE = 10

data_dir = Path('../data/sarp')

# Small barriers
# these data are in CONUS Albers (EPSG:5070)
df = gp.read_file(
    data_dir / 'Road_Related_Barriers_DraftOne_Final08012019.gdb')

# round to the nearest 10 meters in Albers
df['rnd_x'] = (df.geometry.x / TOLERANCE).round().astype('int') * TOLERANCE
df['rnd_y'] = (df.geometry.y / TOLERANCE).round().astype('int') * TOLERANCE
clean = df.drop_duplicates(subset=['rnd_x', 'rnd_y'], keep="first").drop(
    columns=['rnd_x', 'rnd_y'])

duplicates = df.loc[~df.index.isin(clean.index)]

print("Removed {} duplicates".format(len(duplicates)))

clean.to_file(
    data_dir / 'temp/Road_Related_Barriers_DraftOne_Final08012019_no_duplicates.shp')
duplicates.to_file(
    data_dir / 'temp/Road_Related_Barriers_DraftOne_Final08012019_duplicates.shp')


# Dams
df = gp.read_file(data_dir / 'Dams_Webviewer_DraftOne_Final.gdb')
df['rnd_x'] = (df.geometry.x / TOLERANCE).round().astype('int') * TOLERANCE
df['rnd_y'] = (df.geometry.y / TOLERANCE).round().astype('int') * TOLERANCE
clean = df.drop_duplicates(subset=['rnd_x', 'rnd_y'], keep="first").drop(
    columns=['rnd_x', 'rnd_y'])

duplicates = df.loc[~df.index.isin(clean.index)]

print("Removed {} duplicates".format(len(duplicates)))

clean.to_file(data_dir / 'temp/Dams_July2019_no_duplicates.shp')
duplicates.to_file(data_dir / 'temp/Dams_July2019_duplicates.shp')


# Waterfalls
df = gp.read_file(data_dir / 'Waterfalls2019.gdb')

# drop those that are in the wrong coordinate system
df = df.loc[df.geometry.y.abs() <= 90]

# project to Albers
df = df.to_crs({'init': 'epsg:5070'})
df['rnd_x'] = (df.geometry.x / TOLERANCE).round().astype('int') * TOLERANCE
df['rnd_y'] = (df.geometry.y / TOLERANCE).round().astype('int') * TOLERANCE
clean = df.drop_duplicates(subset=['rnd_x', 'rnd_y'], keep="first").drop(
    columns=['rnd_x', 'rnd_y'])

duplicates = df.loc[~df.index.isin(clean.index)]

print("Removed {} duplicates".format(len(duplicates)))
# There should be 0

# clean.to_file(data_dir / 'temp/Waterfalls2019_no_duplicates.shp')
# duplicates.to_file(data_dir / 'temp/Waterfalls2019_duplicates.shp')
