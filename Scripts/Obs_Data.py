# Centroid finder for observational data

#!/usr/bin/env python
# coding: utf-8

# Import necessary modules

import xarray as xr
import rioxarray as rxr
import numpy as np
import pandas as pd
import geojson as gj
from shapely.geometry import shape
import openpyxl
import sys

# Set up system arguments; convert integers as necessary

f=sys.argv[1]
date=int(sys.argv[2])
IHR=sys.argv[3]

if int(h) < 10:
    h = h.zfill(2)

#import the lat/lon grid for the obs data

grid = pd.read_csv('/home/nathane1/research/ObsLatLons.csv')

for r in (('',''),('N','')):
    grid_lat = grid['DDLat'].str.replace(*r)

for s in (('"',''),('W','')):    
    grid_lon = grid['DDLon'].str.replace(*s)

grid_lon = grid_lon.str.strip('0')

grid_lat = pd.to_numeric(grid_lat)
grid_lon = pd.to_numeric(grid_lon)
grid_lat = grid_lat.values.reshape(350,450)
grid_lon = grid_lon.values.reshape(350,450)
grid_lat = pd.DataFrame(data = grid_lat)
grid_lon = pd.DataFrame(data = grid_lon)

#combine lat/lon into a single grid

grid_lat = grid_lat.to_xarray()
grid_lon = grid_lon.to_xarray()
grid_lat = xr.Dataset.to_array(grid_lat)
grid_lon = xr.Dataset.to_array(grid_lon)

grid_lat.name = 'Latitude'
grid_lon.name = 'Longitude'
grid_lon = grid_lon.transpose()

grid_lat = grid_lat.transpose()

#import and manipulate the hourly observational data

obs_data = xr.open_rasterio('/chinook2/nathane1/research/Obs_Data/%s' %(f,))
obs_dataarray = xr.DataArray(obs_data)
obs_dataset = obs_dataarray.to_dataset(name = 'precip')
obs_dataset.rio.write_crs(4326)
obs_dataset += obs_dataset

# reconfigure data structures to prepare for merged dataset

precip = obs_dataset.precip
band = obs_dataset.band
y = obs_dataset.y
x = obs_dataset.x

obs_dataset = xr.merge([obs_dataset,grid_lat,grid_lon])

latitude = obs_dataset.Latitude
longitude = obs_dataset.Longitude
obs_dataset = xr.broadcast(obs_dataset)

obs_dataset = xr.Dataset(data_vars = {"precip":(["band","y","x"],precip)},
                        coords = {"band":(["band"], band),
                                 "y":("y",y),
                                 "x":("x",x),
                                 "latitude":(["y","x"], latitude),
                                 "longitude":(["y","x"],longitude)})

#change dimensions on the data array of precipitation

obs_dataset_full = obs_dataset
obs_dataset_full['precip'].x

#Set coordinates for the dataset
obs_dataset_full.coords['longitude'] = (-1 * (obs_dataset_full.longitude))
obs_dataset_full.coords['latitude'] = obs_dataset_full.latitude

#adding geometries for clipping dataset
geometries = ''' {"type": "Polygon",
        "coordinates": [
        [
[-105.5322845,38.30978502],
[-105.5676655,40.31567018],
[-105.662844,46.19769779],
[-105.6957804,49.54074136],
[-92.97405089,49.54074136],
[-92.97405089,44.92458701],
[-84.76335087,44.92458701],
[-84.76335087,38.30978502],
[-105.5322845,38.30978502]
]
      ]
    }'''
cropping_geometries = [gj.loads(geometries)]
min_x, min_y, max_x, max_y = shape(gj.loads(geometries)).bounds
obs_dataset_full_clipped  = obs_dataset_full.where((obs_dataset_full.longitude<=max_x) & (obs_dataset_full.longitude>=min_x) & (obs_dataset_full.latitude<=max_y) & (obs_dataset_full.latitude>=min_y), drop=True)

obs_dataset_cropped = obs_dataset_full_clipped.squeeze('band')
precip_cropped = obs_dataset_cropped.precip
obs_dataset_cropped['precip']

#Data is weighted across a lat-lon grid, with precipitation as the weighting variable

lon_coord = obs_dataset_cropped.longitude
lat_coord = obs_dataset_cropped.latitude

masked_precip = np.ma.masked_where(precip_cropped <= 0, precip_cropped) 
masked_precip = np.ma.masked_invalid(masked_precip) 

lat_weight = masked_precip * lat_coord
sum_lat_weight = lat_weight.sum()
sum_lat_precip = masked_precip.sum()
lat_centroid = sum_lat_weight/sum_lat_precip

lon_weight = masked_precip * lon_coord
sum_lon_weight = lon_weight.sum()
sum_lon_precip = masked_precip.sum()
lon_centroid = sum_lon_weight/sum_lon_precip

centroids = [lat_centroid, lon_centroid]

#write the data to an excel spreadsheet

centroidbook = openpyxl.load_workbook('/home/nathane1/research/Obscentroids/Obs_Centroids.xlsx')
centroidsheet = centroidbook['0%s_%s' %(date,IHR) ]
centroidsheet.append(centroids)
centroidbook.save('/home/nathane1/research/Obscentroids/Obs_Centroids.xlsx')
print(centroids)
