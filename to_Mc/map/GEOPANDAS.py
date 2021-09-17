import shapefile
#import geopandas as gpd
from shapely.geometry import Point # Point class
from shapely.geometry import shape 
import matplotlib.pyplot as plt
from pyproj import Proj, transform


#x1 = long , y1 = lat, , 
x1, y1 = 102.84365758668105, 16.455296161515648
outProj = Proj(init='epsg:32647')
#print(outProj(x1, y1))
#point1 = Point(out_proj(x1, y1))
#point2 = Point(transform(in_proj, out_proj, x1 ,y1))
#th_boundary = gpd.read_file('./TH_tambon_boundary.shp')
#th_boundary.plot()

shp = shapefile.Reader('./TH_tambon_boundary.shp') #open the shapefile
all_shapes = shp.shapes() # get all the polygons
all_records = shp.records() 
count=0
for i in all_shapes:
    print(count)
    boundary = all_shapes[count] # get a boundary polygon
    #print(boundary)
    if Point(outProj(x1, y1)).within(shape(boundary))==True: # make a point and see if it's in the polygon
    #if Point(point_to_check).within(shape(boundary)):
       province = all_records[count][3]
       Aumphoue = all_records[count][5]
       Tambon = all_records[count][7] # get the second field of the corresponding 
       break
    else:
        #print('shape',shape(boundary))
        print('Point not in shape')
    count += 1
print("province:", province, " Aumphone:",Aumphoue, "Tambon:",Tambon)
    
    