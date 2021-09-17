# -*- coding: utf-8 -*-
# import os, sys
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point
from pyproj import Proj, transform

path = 'D:/LAB/geopandas_tuitor/'


CVM_SSC_PRV = gpd.read_file('D:/Report Focus Area2/CVM_SSC_PRV.shp')
CVM_SSC_PRV.plot()
print(CVM_SSC_PRV.crs)

# Importing Thailand ESRI Shapefile 
# th_boundary = gpd.read_file(path+'TH_amphoe_border.shp')
th_boundary = gpd.read_file('D:/LAB/maclab/TH_tambon_boundary.shp')

#th_boundary.set_crs(epsg=3857, inplace=True)
# th_boundary.plot()

cvm_data = pd.read_csv(path+'CVM_SSC.csv')
inProj = Proj(init='epsg:4326')
outProj = Proj(init='epsg:32647')
#point2 = Point(transform(in_proj, out_proj, x1 ,y1))
df=pd.DataFrame([],columns=['long','lat'])
for v in cvm_data.values:
    long, lat= v[3], v[2]
    outProj = Proj(init='epsg:32647')
    data = outProj(long, lat)
    df2 = pd.DataFrame([data],columns=['long','lat'])
    df = pd.concat([df, df2])
cvm_geo = [Point(xy) for xy in zip(df['long'],df['lat'])]
cvm_point = gpd.GeoDataFrame(cvm_data, geometry = cvm_geo, crs = 32647)
cvm_point.plot()

fig, ax = plt.subplots(figsize = (10,10))
th_boundary.plot(ax=ax,color = 'none', edgecolor = 'green')
cvm_point.plot(ax=ax, markersize = 2, color = 'red')

# Spatial Join 

#cvm_point = gpd.sjoin(CVM_SSC_PRV,cvm_point, how = 'inner', op = 'intersects')

cvm_point2 = gpd.sjoin(th_boundary,cvm_point, how = 'inner', op = 'intersects')
