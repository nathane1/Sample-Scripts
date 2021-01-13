#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import rioxarray as rxr
import numpy as np
import pandas as pd
import geojson as gj
from shapely.geometry import shape
import openpyxl
import sys

#Set input system arguments

date = int(sys.argv[1])
IHR = sys.argv[2]
member = str(sys.argv[3])
h = str(sys.argv[4])
h0 = str(sys.argv[5])

#if int(h) < 10:
 #   h = h.zfill(2)

#rioxarray opens first (newer hour) data file and sets it up for hourly calculation
xds = xr.open_dataset('/chinook2/nathane1/research/HREF_Data/0%s_%s/Regridded/%s/%sHREF_0%s_%s_f%s.nc' %(date,IHR,member,member,date,IHR,h ))
xds = xds.rio.set_spatial_dims(x_dim = 'x', y_dim = 'y')
xds = xds.rio.write_crs(4326)
filled = xds.interp()

#rioxarray opens second (older hour) data file and sets up for hourly calculation
if int(h0) !=0:
    xds2 = xr.open_dataset('/chinook2/nathane1/research/HREF_Data/0%s_%s/Regridded/%s/%sHREF_0%s_%s_f%s.nc' %(date,IHR,member,member,date,IHR,h0 ))
    xds2 = xds2.rio.set_spatial_dims(x_dim = 'x', y_dim = 'y')
    xds2 = xds2.rio.write_crs(4326)
    filled2 = xds2.interp()
else:
    filled2 = None
    
#data is subtracted to receive hourly precipitation data for newer hour
if filled2 is None:
    hourly = filled
else:    
    hourly = filled - filled2
    hourly = hourly.rio.set_spatial_dims(x_dim = 'x', y_dim = 'y')

#adding geometries for clipping dataset
geometries = ''' {"type": "Polygon",
        "coordinates": [
        [
[-83.87271466,38.00537515],
[-85.22781771,35.04711026],
[-88.39725977,35.90371622],
[-91.79513008,36.64610805],
[-95.22155393,37.20290193],
[-102.7991695,37.58837461],
[-102.7991695,47.40041974],
[-79.67678304,47.40041974],
[-79.67678304,45.33874532],
[-81.15046256,43.03372155],
[-82.59717485,40.48293935],
[-83.87271466,38.00537515]
]
]
    }'''
min_x, min_y, max_x, max_y = shape(gj.loads(geometries)).bounds
hourly_clipped  = hourly.where((hourly.lon<=max_x) & (hourly.lon>=min_x) & (hourly.lat<=max_y) & (hourly.lat>=min_y), drop=True)
precip_clipped = hourly['apcpsfc'].where((hourly['apcpsfc'].lon<=max_x) & (hourly['apcpsfc'].lon>=min_x) & (hourly['apcpsfc'].lat<=max_y) & (hourly['apcpsfc'].lat>=min_y), drop=True)

cropping_geometries = [gj.loads(geometries)]

#Data is weighted across a lat-lon grid, with precipitation as the weighting variable

lon_coord = hourly_clipped.lon
lat_coord = hourly_clipped.lat

masked_precip = np.ma.masked_where(precip_clipped == 0, precip_clipped) 
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
print(centroids)

#export the centroid values to an excel file

centroidbook = openpyxl.load_workbook('/home/nathane1/research/HREFcentroids/HREF_Centroids.xlsx')
centroidsheet = centroidbook['0%s_%s' %(date,IHR,)]
centroidsheet.append(centroids)
centroidbook.save('/home/nathane1/research/HREFcentroids/HREF_Centroids.xlsx')
