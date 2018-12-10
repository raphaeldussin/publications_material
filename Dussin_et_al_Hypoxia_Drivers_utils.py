import netCDF4 as nc
import numpy as np
import matplotlib.pylab as plt
import matplotlib.cm as cm
import matplotlib.colors as cl
import matplotlib.ticker as ticker
from mpl_toolkits.basemap import Basemap
from scipy import ndimage as im
from scipy import spatial
import seaborn as sns
import pandas as pd
from terminaltables import AsciiTable

#######################################################################
### Colors/colormaps
#######################################################################

def rt_getcolormaps(file_cb='misc/rt_colormaps.txt'):
    rt_colormaps = dict()
    # Open file
    curr = 0
    with open(file_cb,'r') as f:
        for line in f:
            i_tmp=np.mod(curr,4)
            if (i_tmp==0):
                # The first line is the name of the colormap
                if curr>0:
                    # If not on the first line of file, save previous cm
                    rt_colormaps[name] = cmat2cmpl(val);
                    del(val)
                name=line.strip()
            else:
                # get values of colormap
                line=line.strip()
                cols = line.split(',')
                # if Red values (first column), initialize array
                if (i_tmp == 1):
                    val=np.zeros([3,len(cols)-1])
                val[i_tmp-1,:]=[float(y) for y in cols[0:-1]]
            curr+=1
    return rt_colormaps


def cmat2cmpl(colormap):
    '''
    Convert matlab style colormap to matplotlib style
    Enter a list non normalized RGB values from 0-255
    '''
    r = colormap[0,:]
    g = colormap[1,:]
    b = colormap[2,:]

    cmap = cl.ListedColormap(zip(r,g,b))
    return cmap


def define_colors():
    ''' define my custom colors '''
    my_blue    = np.array([57,106,177]) / 255.
    my_orange  = np.array([218,124,48]) / 255.
    my_green   = np.array([62,150,81])  / 255.
    my_red     = np.array([204,37,41])  / 255.
    my_grey    = np.array([83,81,84])   / 255.
    my_violet  = np.array([107,76,154]) / 255.
    my_darkred = np.array([146,36,40])  / 255.
    my_yellow  = np.array([148,139,61]) / 255.

    my_blue_bar    = np.array([114,147,203]) / 255.
    my_orange_bar  = np.array([225,151,76])  / 255.
    my_green_bar   = np.array([132,186,91])  / 255.
    my_red_bar     = np.array([211,94,96])   / 255.
    my_grey_bar    = np.array([128,133,133]) / 255.
    my_violet_bar  = np.array([144,103,167]) / 255.
    my_darkred_bar = np.array([171,104,87])  / 255.
    my_yellow_bar  = np.array([204,194,16])  / 255.

    my_colors = {'my_blue':my_blue,'my_orange':my_orange,'my_green':my_green,
                 'my_red':my_red,'my_grey':my_grey,'my_violet':my_violet,
                 'my_darkred':my_darkred,'my_yellow':my_yellow,
                 'my_blue_bar':my_blue_bar,'my_orange_bar':my_orange_bar,
                 'my_green_bar':my_green_bar,'my_red_bar':my_red_bar,
                 'my_grey_bar':my_grey_bar,'my_violet_bar':my_violet_bar,
                 'my_darkred_bar':my_darkred_bar,'my_yellow_bar':my_yellow_bar}
    return my_colors

#######################################################################
### I/O
#######################################################################

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def readnc(filein,varin):
    ''' read data from netcdf file '''
    fid = nc.Dataset(filein,'r')
    out = fid.variables[varin][:].squeeze()
    fid.close()
    return out


def pflist(myfloats):
    ''' print friendly list for float or sequence of floats '''
    myfloats = np.array([myfloats]) # needed for single value, doesn't affect sequence
    tmp = np.array_str(myfloats,precision=3)
    out = tmp.replace('[','').replace(']','').split()
    return out


def convert2ma(array):
    out = np.ma.masked_values(array,0.)
    return out

#######################################################################
### Plotting functions
#######################################################################

def add_etopo(datadir, bmap):
    ''' add etopo land topography '''
    paltopo = cm.binary
    lon_topo = readnc(datadir + 'etopo_ccs.nc','topo_lon') + 360.
    lat_topo = readnc(datadir + 'etopo_ccs.nc','topo_lat')
    lon_topo2, lat_topo2 = np.meshgrid(lon_topo, lat_topo)
    topo = readnc(datadir + 'etopo_ccs.nc', 'topo')
    topomin=0 ; topomax=4000
    topo = np.ma.masked_less_equal(topo, 0.)
    normtopo = cl.Normalize(vmin=topomin, vmax=topomax)
    xtopo, ytopo = bmap(lon_topo2, lat_topo2)
    T = bmap.contourf(xtopo, ytopo, topo, 100, cmap=paltopo, norm=normtopo)
    return bmap


def add_grid(bmap, parallels, meridians, hide_grid=False):
    ''' add longitude/latitude '''
    if hide_grid:
        bmap.drawparallels(parallels, labels=[False,False,False,False],
                           linewidth=1, color=[1.,1.,1.])
        bmap.drawmeridians(meridians, labels=[False,False,False,False],
                           linewidth=1, color=[1.,1.,1.])
    else:
        bmap.drawparallels(parallels, labels=[True,False,False,True],
                           linewidth=1, color=[0.6,0.6,0.6], fontsize=20)
        bmap.drawmeridians(meridians, labels=[True,False,False,True],
                           linewidth=1, color=[0.6,0.6,0.6], fontsize=20)
        bmap.drawcoastlines()
    return bmap


def setup_map(datadir, plt_topo=True,hide_grid=False):
    ''' set the map, with etopo optionally '''
    # background
    bmap = Basemap(projection='cyl',llcrnrlat=18,urcrnrlat=51,
                   llcrnrlon=219,urcrnrlon=251,resolution='l')
    parallels = np.arange(20.,60.,10.)
    meridians = np.arange(220.,260.,10.)
    bmap = add_grid(bmap, parallels, meridians, hide_grid=hide_grid)
    if plt_topo:
        bmap = add_etopo(datadir, bmap)
    return bmap


def setup_map_small(datadir, plt_topo=True,hide_grid=False):
    ''' set the map, with etopo optionally '''
    # background
    bmap = Basemap(projection='cyl',llcrnrlat=20,urcrnrlat=50,
                   llcrnrlon=220,urcrnrlon=250,resolution='l')
    parallels = np.arange(25.,55.,10.)
    meridians = np.arange(220.,260.,10.)
    bmap = add_grid(bmap, parallels, meridians, hide_grid=hide_grid)
    if plt_topo:
        bmap = add_etopo(datadir, bmap)
    return bmap


def setup_map_verysmall(datadir, plt_topo=True,hide_grid=False):
    ''' set the map, with etopo optionally '''
    # background
    bmap = Basemap(projection='cyl',llcrnrlat=30,urcrnrlat=45,
                   llcrnrlon=230,urcrnrlon=240,resolution='l')
    parallels = np.arange(35.,55.,5.)
    meridians = np.arange(220.,260.,5.)
    bmap = add_grid(bmap, parallels, meridians, hide_grid=hide_grid)
    if plt_topo:
        bmap = add_etopo(datadir, bmap)
    return bmap
