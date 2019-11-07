from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import astropy.table as tbl
from typing import Union


def plot_globe(file, centre_lat=0, centre_lon=0, show=True):
    bmap = Basemap(projection='ortho', lat_0=centre_lat, lon_0=centre_lon, resolution='l', area_thresh=1000.)
    bmap.warpimage(image=file)
    bmap.drawmapboundary()
    bmap.drawmeridians(np.arange(0, 360, 30))
    bmap.drawparallels(np.arange(-90, 90, 30))

    if show:
        plt.show()

    return bmap


def plot_map(file, show=True, projection='cyl'):
    bmap = Basemap(projection=projection, llcrnrlat=-90, urcrnrlat=90, \
                   llcrnrlon=-180, urcrnrlon=180, resolution='c')
    bmap.warpimage(image=file)
    bmap.drawmeridians(np.arange(0, 360, 30))
    bmap.drawparallels(np.arange(-90, 90, 30))

    if show:
        plt.show()

    return bmap


location_types = ['city', 'natural']


class Location:
    def __init__(self, name: str = None, lon: float = None, lat: float = None, typ: str = None):
        self.name = name
        self.lon = lon
        self.lat = lat
        self.typ = typ


marker_colours = ['r', 'g', 'b']


class Map:
    def __init__(self, image: str, locations: str = None):
        self.image = image
        self.locations_path = locations
        if locations is not None:
            self.locations_tbl = tbl.Table.read(locations, format='ascii.csv')
        else:
            self.locations_tbl = tbl.Table()
        self.locations = {}
        self.create_locations()

    def create_locations(self):
        for loc in self.locations_tbl:
            print(loc)
            if loc['type'] not in self.locations:
                self.locations[loc['type']] = []
            location = Location(name=loc['name'], lon=loc['longitude'], lat=loc['latitude'], typ=loc['type'])
            self.locations[loc['type']].append(location)

    def plot_locations(self, types: Union[list, str] = None, centre_lat=0, centre_lon=0, projection='ortho'):
        if type(types) is str:
            types = [types]
        elif types is None:
            types = self.locations.keys()

        if projection == 'ortho':
            bmap = plot_globe(file=self.image, centre_lat=centre_lat, centre_lon=centre_lon, show=False)
        else:
            bmap = plot_map(file=self.image, show=False, projection=projection)

        for i, typ in enumerate(types):
            for loc in self.locations[typ]:
                bmap.plot(loc.lon, loc.lat, f'{marker_colours[i]}o', latlon=True)
                plt.text(loc.lon, loc.lat, loc.name, c=marker_colours[i], fontsize=8)
        plt.show()
