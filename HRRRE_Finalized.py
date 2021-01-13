import xarray as xr
import rioxarray as rxr
import numpy as np
import pandas as pd
import geojson as gj
from shapely.geometry import shape
import openpyxl
import sys

#Set the date as two arguments and the initialization hour

date = int(sys.argv[1])
IHR = sys.argv[2]
member = int(sys.argv[3])
h = str(sys.argv[4])
h0 = str(sys.argv[5])

if int(h) < 10:
    h = h.zfill(2)
if int(h0) < 10:
    h0 =h0.zfill(2)

#rioxarray opens first (newer hour) data file and sets it up for hourly calculation
if int(h0) !=0:
    xds = xr.open_rasterio("/chinook2/nathane1/research/Hrrre_Data/0%s_%sz/mem0%s/qpfOnly/HRRRE_0%s_%s_f%s.nc" %(date,IHR,member,date,IHR,h, ))
    xds = xds.rio.write_crs(4326)
    filled = xds.rio.interpolate_na()
else:    
    xds = xr.open_dataset("/chinook2/nathane1/research/Hrrre_Data/0%s_%sz/mem0%s/qpfOnly/HRRRE_0%s_%s_f%s.nc" %(date,IHR,member,date,IHR,h, ))
    xds = xds.rio.write_crs(4326)
    filled = xds.rio.interpolate_na()    

#rioxarray opens second (older hour) data file and sets up for hourly calculation
if int(h0) != 0:
    xds2 = xr.open_dataset("/chinook2/nathane1/research/Hrrre_Data/0%s_%sz/mem0%s/qpfOnly/HRRRE_0%s_%s_f%s.nc" %(date,IHR,member,date,IHR,h0, ))
    xds2 = xds2.rio.write_crs(4326)
    filled2 = xds2.rio.interpolate_na()
else:
    filled2 = None
    hourly = filled

#data is subtracted to receive hourly precipitation data for newer hour
if filled2 is None:
    hourly = filled
else:
    hourly = filled - filled2

#hourly = hourly.rename({'var0_1_227_surface':'APCP_surface'})
hourly_precip = hourly.APCP_surface
hourly.coords['Longitude'] = (-1 * (360 - hourly.longitude))
hourly.coords['Latitude'] = hourly.latitude
hourly_precip.coords['Longitude'] = (-1 * (360 - hourly.longitude))
hourly_precip.coords['Latitude'] = hourly.latitude

#adding geometries for clipping dataset
geometries = ''' {"type": "Polygon",
        "coordinates": [
        [
[-84.01243265,37.72399023],
[-99.71035882,37.72399023],
[-99.71035882,48.74089469],
[-82.84682434,48.74089469],
[-81.38624859,48.32986263],
[-78.64439567,47.47799576],
[-78.64583253,46.82004424],
[-79.85764318,45.08992904],
[-81.44335565,42.53825454],
[-82.77699596,40.16006258],
[-84.01243265,37.72399023]        
        ]
]
    }'''
min_x, min_y, max_x, max_y = shape(gj.loads(geometries)).bounds
hourly_clipped  = hourly.where((hourly.Longitude<=max_x) & (hourly.Longitude>=min_x) & (hourly.Latitude<=max_y) & (hourly.Latitude>=min_y), drop=True)
precip_clipped = hourly_precip.where((hourly_precip.Longitude<=max_x) & (hourly_precip.Longitude>=min_x) & (hourly_precip.Latitude<=max_y) & (hourly_precip.Latitude>=min_y), drop=True)

#squeeze clipped precipitation to have the correct shape
if int(h0) != 0:
    precip_clipped = precip_clipped.squeeze('band')
    precip_clipped = precip_clipped.squeeze('time')
else: 
    pass

#Data is weighted across a lat-lon grid, with precipitation as the weighting variable

lon_coord = hourly_clipped.Longitude
lat_coord = hourly_clipped.Latitude

masked_precip = np.ma.masked_where(precip_clipped <= 0, precip_clipped)
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

centroidbook = openpyxl.load_workbook ('/home/nathane1/research/HRRREcentroids/HRRRE_Centroids.xlsx')
centroidsheet = centroidbook['0%s_%s' %(date,IHR,)]
centroidsheet.append(centroids)
centroidbook.save('/home/nathane1/research/HRRREcentroids/HRRRE_Centroids.xlsx')
