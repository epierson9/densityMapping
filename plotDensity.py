def makeNearestNeighborsDensityPlot(d, col_of_interest, title_string, color_min = 0, color_max = 1, n_neighbors = 50, center_around_america = True, res = .2):
    cmap = 'bwr'
    t0 = time.time()
    if center_around_america:
        min_lat = 15
        max_lat = 50
        min_long = -130
        max_long = -65
    else:
        #center around europe
        min_lat = 35
        max_lat = 70
        min_long = -20
        max_long = 50
    geolocated = d.dropna(subset = ['lat', 'lon']) 
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
    m = Basemap(llcrnrlat=min_lat,
                    urcrnrlat=max_lat, llcrnrlon=min_long,
                    urcrnrlon=max_long, resolution='l', fix_aspect = False)
    data_to_eval = np.hstack([unraveled_x, unraveled_y])
    m.drawcoastlines()
    #m.fillcontinents(color='coral',lake_color='aqua')
    x, y = m(data_to_eval[:,1], data_to_eval[:,0])
    loc = np.c_[x, y]
    polys = [p.boundary for p in m.landpolygons]
    on_land = points_in_polys(loc, polys) 
    density = model.predict_proba(data_to_eval)[:, 1]
    max_density = density.max()
    density[~on_land] = max_density / 2
    density = density.reshape(X.shape)
    
    
    #Basemap.is_land([1, 2])
    if color_max is None:
        color_max = max_density
    cset1 = contourf(Y, X, density, levels = np.linspace(color_min, color_max, 25))
    
    m.drawcoastlines(linewidth = 2)
    m.drawcountries(linewidth = 2)
    m.drawstates(linewidth = 2)
    title(title_string, fontsize = 30, fontweight = 'bold')
    

    colorbar()
    print 'Time to make plot', time.time() - t0
    set_cmap(cmap)
    savefig('%s' % title_string, dpi = 300, format = 'png')
    show()
