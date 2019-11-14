from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import astropy.table as tbl
from typing import Union
from math import *
import imageio


# TODO: Interact directly with SVG?

def plot_globe(file: str, centre_lat: float = 0, centre_lon: float = 0, show=True):
    """
    Using an image file and basemap, creates an orthographic projection of the image. Assumes the image is in a
    cylindrical projection.
    :param file: Path to the image file.
    :param centre_lat: Latitude to show at centre.
    :param centre_lon: Longitude to show at centre.
    :param show: Set to True to show the plot.
    :return: Basemap object of map.
    """
    # Set up basemap object.
    bmap = Basemap(projection='ortho', lat_0=centre_lat, lon_0=centre_lon, resolution='l', area_thresh=1000.)
    # Draw plot.
    bmap.warpimage(image=file)
    bmap.drawmapboundary()
    bmap.drawmeridians(np.arange(0, 360, 30))
    bmap.drawparallels(np.arange(-90, 90, 30))

    if show:
        plt.show()

    return bmap


def plot_map(file: str, centre_lat: float = 0, centre_lon: float = 0, show: float = True, projection: str = 'cyl'):
    """
    Using an image file and basemap, plots the map to the projection specified. Projections should be those supported in
    Basemap; not all projections will work.
    :param file: Path to the image file.
    :param centre_lat: Latitude to show at centre.
    :param centre_lon: Longitude to show at centre.
    :param show: Set to True to show the plot.
    :param projection: Projection type, as listed at https://matplotlib.org/basemap/users/mapsetup.html
    :return: Basemap object for this map.
    """
    # Set up basemap object.
    bmap = Basemap(projection=projection, llcrnrlat=-90, urcrnrlat=90,
                   llcrnrlon=-180, urcrnrlon=180, resolution='c',
                   lat_0=centre_lat, lon_0=centre_lon)
    # Draw plot.
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
    :return: float, great circle angular distance, in radians.
    """

    # Convert to radians.
    if deg:
        lon1 = radians(lon1)
        lon2 = radians(lon2)
        lat1 = radians(lat1)
        lat2 = radians(lat2)

    delta_lon = lon2 - lon1
    # Perform calculation.
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
    :return: float, great circle distance, in metres.
    """
    # Calculate great circle angular distance.
    ang_dist = great_circle_ang_dist(lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2, deg=deg)
    # Multiply by radius of planet.
    return radius * ang_dist


location_types = ['city', 'natural']


class Location:
    def __init__(self, name: str = None, lon: float = None, lat: float = None, typ: str = None, this_map: "Map" = None):
        """

        :param name: Name of location.
        :param lon: Longitude of location.
        :param lat: Latitude of location.
        :param typ: Type of location.
        :param this_map: The Map object on which this location belongs.
        """
        self.name = name
        self.lon = lon
        self.lat = lat
        self.type = typ
        self.map = this_map

    def __str__(self):
        return f"{self.name}; {self.type} at longitude = {self.lon}, latitude = {self.lat}"

    def distance_to(self, other):
        """
        Calculates the great circle distance from this location to another location object, assuming both are on the
        same Map, in metres. All units are interpreted as degrees unless deg is given as False, in which case all units
        are interpreted as radians.
        Constructed using https://en.wikipedia.org/wiki/Great-circle_distance
        :param other: other location object.
        :return: float, great circle distance, in metres.
        """
        if self.map is not None:
            return great_circle_distance(lon1=self.lon, lat1=self.lat, lon2=other.lon, lat2=other.lat,
                                         radius=self.map.planet_radius)
        else:
            return great_circle_distance(lon1=self.lon, lat1=self.lat, lon2=other.lon, lat2=other.lat)


marker_colours = ['r', 'g', 'b']


class Map:
    def __init__(self, image: str, locations: str = None, planet_radius: float = 6371e3):
        """

        :param image: Path to image file of map.
        :param locations: Path to csv file containing spreadsheet of locations.
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
        """
        Read locations from csv file into this Map.
        :return:
        """
        for loc in self.locations_tbl:
            print(loc)
            if loc['type'] not in self.locations:
                self.locations[loc['type']] = []
            location = Location(name=loc['name'], lon=loc['longitude'], lat=loc['latitude'], typ=loc['type'])
            self.locations[loc['type']].append(location)

    def plot_map(self, centre_lat: float = 0, centre_lon: float = 0, projection: str = 'ortho', output: str = None,
                 show: bool = False):
        """
        Plots this map.
        :param centre_lat: Latitude to show at centre.
        :param centre_lon: Longitude to show at centre.
        :param projection: Projection type, as listed at https://matplotlib.org/basemap/users/mapsetup.html
        :param output: Path to which to save the plot.
        :param show: Set to True to show the plot.
        :return: Basemap object for this map.
        """
        if projection == 'ortho':
            bmap = plot_globe(file=self.image, centre_lat=centre_lat, centre_lon=centre_lon, show=False)
        else:
            bmap = plot_map(file=self.image, centre_lat=centre_lat, centre_lon=centre_lon, show=False,
                            projection=projection)
        if output is not None:
            plt.savefig(output)
        if show:
            plt.show()
        return bmap

    def plot_gif(self, output: str, centre_lat: float = 0, lon_interval: int = 10):
        """
        Plot an animated, rotating gif of the map.
        :param output: Path to which to save the frames and final gif.
        :param centre_lat: Latitude to show at centre.
        :param lon_interval: Longitude interval between frames.
        :return: list of image objects.
        """
        images = []
        for lon in range(0, 360, lon_interval):
            filename = output + str(lon) + '.png'
            self.plot_map(centre_lat=centre_lat, centre_lon=lon, projection='ortho', output=filename, show=False)
            plt.close()
            print(filename)
            images.append(imageio.imread(filename))
        imageio.mimsave(output + 'rotating.gif', images)
        return images

    def plot_locations(self, types: Union[list, str] = None, centre_lat=0, centre_lon=0, projection='ortho',
                       fontsize=10, output: str = None):
        """
        Plot the locations associated with this Map over the map image.
        :param types:
        :param centre_lat: Latitude to show at centre.
        :param centre_lon: Longitude to show at centre.
        :param projection: Projection type, as listed at https://matplotlib.org/basemap/users/mapsetup.html
        :param fontsize: Size of font for labels.
        :param output: Path to which to save the plot.
        """
        if type(types) is str:
            types = [types]
        elif types is None:
            types = self.locations.keys()

        bmap = self.plot_map(centre_lat=centre_lat, centre_lon=centre_lon, projection=projection, output=None)

        for i, typ in enumerate(types):
            for loc in self.locations[typ]:
                bmap.plot(loc.lon, loc.lat, f'{marker_colours[i]}o', latlon=True)
                plt.text(loc.lon, loc.lat, loc.name, c=marker_colours[i], fontsize=fontsize)
        if output is not None:
            plt.savefig(output)
        plt.show()
