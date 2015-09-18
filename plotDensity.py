from sklearn.neighbors import KNeighborsClassifier 
from matplotlib import path
import random
from mpl_toolkits.basemap import Basemap 
import numpy as np
import pandas as pd
from pylab import *

def pnpoly(x, y, xyverts):
    """
    Included code for this matplotlib method directly in file b/c some versions don't have it. 
    inside = pnpoly(x, y, xyverts)
    Return 1 if x,y is inside the polygon, 0 otherwise.
    *xyverts*
        a sequence of x,y vertices.
    A point on the boundary may be treated as inside or outside.
    .. deprecated:: 1.2.0
        Use :meth:`~matplotlib.path.Path.contains_point` instead.
    """
    p = path.Path(xyverts)
    return p.contains_point([x, y])

def points_inside_poly(xypoints, xyverts):
    """
    Included code for this matplotlib method directly in file b/c some versions don't have it. 
    mask = points_inside_poly(xypoints, xyverts)
    Returns a boolean ndarray, True for points inside the polygon.
    *xypoints*
        a sequence of N x,y pairs.
    *xyverts*
        sequence of x,y vertices of the polygon.
    A point on the boundary may be treated as inside or outside.
    .. deprecated:: 1.2.0
        Use :meth:`~matplotlib.path.Path.contains_points` instead.
    """
    p = path.Path(xyverts)
    return p.contains_points(xypoints)


def points_in_polys(points, polys):
    """
    This method masks off the water (where data will be unreliable).
    """
    result = []
    for i, poly in enumerate(polys):
        if i == 0:
            mask = points_inside_poly(points, poly)
        else:
            mask = mask | points_inside_poly(points, poly)
    return np.array(mask)

def makeNearestNeighborsDensityPlot(filename, col_of_interest, title_string = None, min_lat = 15, max_lat = 50, min_long = -130, max_long = -65, maskOffWater = True, cmap = 'bwr', color_min = 0, color_max = 1, n_neighbors = 5, center_around_america = True, res = .2):
    d = pd.read_csv(filename)
    geolocated = d.dropna(subset = ['lat', 'lon', col_of_interest]) 
    idxs = (geolocated['lat'] > min_lat) & (geolocated['lat'] < max_lat) 
    idxs = idxs &  (geolocated['lon'] > min_long) & (geolocated['lon'] < max_long) 
    geolocated = geolocated.loc[idxs]
    model = KNeighborsClassifier(n_neighbors = n_neighbors)
    print 'Total number of points', len(geolocated), 'in column of interest nonzero', geolocated[col_of_interest].sum()
    model.fit(geolocated[['lat', 'lon']], geolocated[col_of_interest])
    
    x = np.arange(min_lat, max_lat, res)
    y = np.arange(min_long, max_long, res)
    X, Y = meshgrid(x, y)
    numel = len(X) * len(X[0, :])
    Z = np.zeros(X.shape)
    unraveled_x = X.reshape([numel, 1])
    unraveled_y = Y.reshape([numel, 1])
    figure(figsize = [20, 10])
    m = Basemap(llcrnrlat=min_lat, urcrnrlat=max_lat, llcrnrlon=min_long, urcrnrlon=max_long, resolution='l', fix_aspect = False)
    data_to_eval = np.hstack([unraveled_x, unraveled_y])
    
    if maskOffWater:
        m.drawcoastlines()
        x, y = m(data_to_eval[:,1], data_to_eval[:,0])
        loc = np.c_[x, y]
        polys = [p.boundary for p in m.landpolygons]
        on_land = points_in_polys(loc, polys) 
        density = model.predict_proba(data_to_eval)[:, 1]
        max_density = density.max()
        density[~on_land] = max_density / 2
    
    density = density.reshape(X.shape)
    cset1 = contourf(Y, X, density, levels = np.linspace(color_min, color_max, 25))
    
    m.drawcoastlines(linewidth = 2)
    m.drawcountries(linewidth = 2)
    m.drawstates(linewidth = 2)
    
    colorbar()
    set_cmap(cmap)
    if title_string is not None:
        title(title_string, fontsize = 30, fontweight = 'bold')
        savefig('%s' % title_string, dpi = 300, format = 'png')
    else:
        savefig('plot.png', dpi = 300, format = 'png')
    show()
def generateSimulatedData():
    lats = list(35 + (np.random.random([2000,]) - .5) * 10)
    longs = list(-100 + (np.random.random([1000,]) - .5) * 20) + list(-80 + (np.random.random([1000,]) - .5) * 20)
    is_pizza_shop = [1 for i in range(1000)] + [0 for i in range(1000)] 
    d = pd.DataFrame({'lat':lats, 'lon':longs, 'pizza_shops':is_pizza_shop})
    d.to_csv('sample_data.csv', index_col = False)

if __name__ == '__main__':
    generateSimulatedData()
    filename = 'sample_data.csv'
    col_of_interest = 'pizza_shops'
    makeNearestNeighborsDensityPlot(filename, col_of_interest)


