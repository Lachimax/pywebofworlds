from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import astropy.table as tbl
from typing import Union
from math import *


def plot_globe(file, centre_lat=0, centre_lon=0, show=True):
    bmap = Basemap(projection='ortho', lat_0=centre_lat, lon_0=centre_lon, resolution='l', area_thresh=1000.)
    bmap.warpimage(image=file)
    bmap.drawmapboundary()
    bmap.drawmeridians(np.arange(0, 360, 30))
    bmap.drawparallels(np.arange(-90, 90, 30))

    if show:
        plt.show()

    return bmap


def plot_map(file, centre_lat=0, centre_lon=0, show=True, projection='cyl'):
    bmap = Basemap(projection=projection, llcrnrlat=-90, urcrnrlat=90,
                   llcrnrlon=-180, urcrnrlon=180, resolution='c',
                   lat_0=centre_lat, lon_0=centre_lon)
    bmap.warpimage(image=file)
    bmap.drawmeridians(np.arange(0, 360, 30))
    bmap.drawparallels(np.arange(-90, 90, 30))

    if show:
        plt.show()

    return bmap


def great_circle_ang_dist(lon1: float, lat1: float, lon2: float, lat2: float, deg: bool = True):
    """
    Calculates the great circle angular distance between two points on the map, in degrees. All units are interpreted as
    degrees unless deg is given as False, in which case all units are interpreted as radians.
    Constructed using https://en.wikipedia.org/wiki/Great-circle_distance
    :param lon1: Longitude of first point.
    :param lat1: Latitude of first point.
    :param lon2: Longitude of second point.
    :param lat2: Latitude of second points.
    :param deg: Interpret units as degrees? If False, interprets as radians.
    :return:
    """

    # Convert to radians.
    if deg:
        lon1 = radians(lon1)
        lon2 = radians(lon2)
        lat1 = radians(lat1)
        lat2 = radians(lat2)

    delta_lon = lon2 - lon1
    return acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(delta_lon))


def great_circle_distance(lon1: float, lat1: float, lon2: float, lat2: float, radius: float = 6371e3, deg: bool = True):
    """
    Calculates the great circle distance between two points on the map, in metres. All units are interpreted as degrees
    unless deg is given as False, in which case all units are interpreted as radians.
    Constructed using https://en.wikipedia.org/wiki/Great-circle_distance
    :param lon1: Longitude of first point.
    :param lat1: Latitude of first point.
    :param lon2: Longitude of second point.
    :param lat2: Latitude of second points.
    :param deg: Interpret units as degrees? If False, interprets as radians.
    :param radius: Radius of the planet.
    :return:
    """
    ang_dist = great_circle_ang_dist(lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2, deg=deg)
    return radius * ang_dist


location_types = ['city', 'natural']


class Location:
    def __init__(self, name: str = None, lon: float = None, lat: float = None, typ: str = None):
        self.name = name
        self.lon = lon
        self.lat = lat
        self.typ = typ


marker_colours = ['r', 'g', 'b']


class Map:
    def __init__(self, image: str, locations: str = None, planet_radius: float = 6371e3):
        """

        :param image:
        :param locations:
        :param planet_radius: In metres.
        """
        self.image = image
        self.locations_path = locations
        self.planet_radius = planet_radius
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

    def plot_locations(self, types: Union[list, str] = None, centre_lat=0, centre_lon=0, projection='ortho',
                       fontsize=10):
        if type(types) is str:
            types = [types]
        elif types is None:
            types = self.locations.keys()

        if projection == 'ortho':
            bmap = plot_globe(file=self.image, centre_lat=centre_lat, centre_lon=centre_lon, show=False)
        else:
            bmap = plot_map(file=self.image, centre_lat=centre_lat, centre_lon=centre_lon, show=False,
                            projection=projection)

        for i, typ in enumerate(types):
            for loc in self.locations[typ]:
                bmap.plot(loc.lon, loc.lat, f'{marker_colours[i]}o', latlon=True)
                plt.text(loc.lon, loc.lat, loc.name, c=marker_colours[i], fontsize=fontsize)
        plt.show()
