from matplotlib import pyplot as plt

# TODO: Move over to cartopy

try:
    from mpl_toolkits.basemap import Basemap

    bmap_available = True
except ImportError:
    print("basemap not installed. Map plotting will not be available.")
    bmap_available = False
import numpy as np
from typing import Union, List
from math import *
import imageio

from astropy import units as un
import astropy.table as tbl

from pywebofworlds.physics import units as u


# TODO: Interact directly with SVG?
# TODO: Journey class; interact with date system in timelines
# Insert function (work like list)

def check_basemap():
    if not bmap_available:
        print("basemap is not installed; map plotting is unavailable.")
    return bmap_available


def lon_lat_from_x_y(x: float, y: float, scale=100):
    """
    Take map coordinates and convert them to latitude and longitude. Assumes a cylindrical projection with lat=0,
    long=0 at the centre of the map.
    :param x: x-coordinate on map
    :param y: y-coordinate on map
    :param scale: The conversion factor between the coordinates on the map and longitude and latitude.
    :return:
    """
    lat = y / scale - 90
    lon = x / scale - 180

    return lon, lat


def x_y_from_lon_lat(lat, lon, scale=100):
    """
    Take latitude and longitude and converts them into map coordinates, assuming a cylindrical projection with lat=0,
    lon=0 at the centre of the map.
    :param lat: Latitude of point.
    :param lon: Longitude of point.
    :param scale: The conversion factor between the coordinates on the map and longitude and latitude.
    :return:
    """
    x = (lon + 180) * scale
    y = (lat + 90) * scale

    return x, y


def plot_globe(file: str, centre_lat: float = 0, centre_lon: float = 0, show: bool = True, meridians: bool = True,
               parallels: bool = True):
    """
    Using an image file and basemap, creates an orthographic projection of the image. Assumes the image is in a
    cylindrical projection.
    :param file: Path to the image file.
    :param centre_lat: Latitude to show at centre.
    :param centre_lon: Longitude to show at centre.
    :param show: Set to True to show the plot.
    :param meridians: set to True to plot meridian lines.
    :param parallels: Set to True to plot parallel lines.
    :return: Basemap object of map.
    """
    # Set up basemap object.
    if not check_basemap():
        return None
    bmap = Basemap(projection='ortho', lat_0=centre_lat, lon_0=centre_lon, resolution='l', area_thresh=1000.)
    # Draw plot.
    bmap.warpimage(image=file)
    bmap.drawmapboundary()
    if meridians:
        bmap.drawmeridians(np.arange(0, 360, 30))
    if parallels:
        bmap.drawparallels(np.arange(-90, 90, 30))
    if show:
        plt.show()

    return bmap


def plot_map(file: str, centre_lat: float = 0, centre_lon: float = 0, show: float = True, projection: str = 'cyl',
             meridians: bool = True, parallels: bool = True):
    """
    Using an image file and basemap, plots the map to the projection specified. Projections should be those supported in
    Basemap; not all projections will work.
    :param file: Path to the image file.
    :param centre_lat: Latitude to show at centre.
    :param centre_lon: Longitude to show at centre.
    :param show: Set to True to show the plot.
    :param meridians: set to True to plot meridian lines.
    :param parallels: Set to True to plot parallel lines.
    :param projection: Projection type, as listed at https://matplotlib.org/basemap/users/mapsetup.html
    :return: Basemap object for this map.
    """
    if not check_basemap():
        return None
    # Set up basemap object.
    bmap = Basemap(projection=projection, llcrnrlat=-90, urcrnrlat=90,
                   llcrnrlon=-180, urcrnrlon=180, resolution='c',
                   lat_0=centre_lat, lon_0=centre_lon)
    # Draw plot.
    bmap.warpimage(image=file)
    if meridians:
        bmap.drawmeridians(np.arange(0, 360, 30))
    if parallels:
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
    :param radius: Radius of the planet, in metres.
    :return: float, great circle distance, in metres.
    """
    if type(radius) is not un.Quantity:
        radius *= un.m
    # Calculate great circle angular distance.
    ang_dist = great_circle_ang_dist(lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2, deg=deg)
    # Multiply by radius of planet.
    return radius * ang_dist


def travel_to(lon: float, lat: float, direction: float, radius: float = 6371e3):
    """

    :param lon:
    :param lat:
    :param direction: In degrees.
    :param radius:
    :return:
    """


location_types = ['city', 'natural']


class Location:
    def __init__(self, name: str = None, lon: float = None, lat: float = None, typ: str = None, this_map: "Map" = None,
                 nxt: "Location" = None, previous: "Location" = None):
        """

        :param name: Name of location.
        :param lon: Longitude of location.
        :param lat: Latitude of location.
        :param typ: Type of location.
        :param this_map: The Map object on which this location belongs.
        :param nxt: The next location. Used when Location is part of a Journey, to link one Location to the next.
        """
        self.name = name
        self.lon = lon
        self.lat = lat
        self.type = typ
        self.map = this_map
        if self.map is not None:
            self.map.add_location(self)

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
            distance = great_circle_distance(lon1=self.lon, lat1=self.lat, lon2=other.lon, lat2=other.lat,
                                             radius=self.map.planet_radius)
        else:
            distance = great_circle_distance(lon1=self.lon, lat1=self.lat, lon2=other.lon, lat2=other.lat)
        return distance

    def travel_time(self, other, speed: float = 4., units: str = "m/s"):
        """

        :param other:
        :param speed:
        :param units:
        :return:
        """
        if speed is not un.Quantity:
            speed = un.Quantity(speed, units)
        distance = self.distance_to(other)
        # u.velocity_to_m_s(v=speed, units=units)
        time = distance / speed
        return time

    def travel_days(self, other, speed: float = 4., units: str = "km/h", time_per_day: float = 7.5):
        """

        :param other:
        :param speed:
        :param units:
        :param time_per_day: In hours.
        :return:
        """
        if type(speed) is not un.Quantity:
            speed = speed * un.km / un.hour
        else:
            speed = speed.to(un.km / un.hour)  # u.velocity_to_velocity(velocity=speed, frm=units, to='kph')
        time = self.travel_time(other=other, speed=speed, units=units)
        if type(time_per_day) is not un.Quantity:
            time_per_day = time_per_day * un.hour / un.day
        else:
            time_per_day = time_per_day.to(un.hour / un.day)  # u.time_to_sec(time=time_per_day, units="hr")
        days = time / time_per_day
        return days.to(un.day)

    def travel_days_dpd(self, other, distance_per_day: float = 30., units: str = "km"):
        """

        :param other:
        :param distance_per_day:
        :param units:
        :return:
        """
        distance = self.distance_to(other)
        distance_per_day = u.length_to_metre(length=distance_per_day, units=units)
        days = distance / distance_per_day
        return days


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

    def add_location(self, location: Location):
        """
        Add a location to this map's internal list of Locations.
        :param location: Location object.
        :return:
        """
        # Set location's map pointer to this map.
        location.map = self
        #
        self.create_location_type_list(location.type)
        self.locations[location.type].append(location)

    def create_location_type_list(self, typ):
        """
        Utility function; checks if there is a list with the name given in self.locations, and creates it if not.
        :param typ: Name of location type
        :return:
        """
        if typ not in self.locations:
            self.locations[typ] = []

    def create_locations(self):
        """
        Read locations from csv file into this Map.
        :return:
        """
        for loc in self.locations_tbl:
            print(loc)
            location = Location(name=loc['name'], lon=loc['longitude'], lat=loc['latitude'], typ=loc['type'])
            self.add_location(location)

    def plot_map(self, centre_lat: float = 0, centre_lon: float = 0, projection: str = 'ortho', output: str = None,
                 show: bool = False, meridians: bool = True, parallels: bool = True):
        """
        Plots this map.
        :param centre_lat: Latitude to show at centre.
        :param centre_lon: Longitude to show at centre.
        :param projection: Projection type, as listed at https://matplotlib.org/basemap/users/mapsetup.html
        :param output: Path to which to save the plot.
        :param show: Set to True to show the plot.
        :param meridians: set to True to plot meridian lines.
        :param parallels: Set to True to plot parallel lines.
        :return: Basemap object for this map.
        """
        if projection == 'ortho':
            bmap = plot_globe(file=self.image, centre_lat=centre_lat, centre_lon=centre_lon, show=False,
                              meridians=meridians, parallels=parallels)
        else:
            bmap = plot_map(file=self.image, centre_lat=centre_lat, centre_lon=centre_lon, show=False,
                            projection=projection, meridians=meridians, parallels=parallels)
        if output is not None:
            plt.savefig(output)
        if show:
            plt.show()
        return bmap

    def plot_gif(self, output: str, centre_lat: float = 0, lon_interval: int = 10, meridians: bool = True,
                 parallels: bool = True):
        """
        Plot an animated, rotating gif of the map.
        :param output: Path to which to save the frames and final gif.
        :param centre_lat: Latitude to show at centre.
        :param lon_interval: Longitude interval between frames.
        :param meridians: set to True to plot meridian lines.
        :param parallels: Set to True to plot parallel lines.
        :return: list of image objects.
        """
        images = []
        for lon in range(0, 360, lon_interval):
            filename = output + str(lon) + '.png'
            self.plot_map(centre_lat=centre_lat, centre_lon=lon, projection='ortho', output=filename, show=False,
                          meridians=meridians, parallels=parallels)
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


class JourneyLocation:
    def __init__(self, location: Location, nxt: "JourneyLocation" = None, previous: "JourneyLocation" = None):
        self.location = location
        self.next = None
        if nxt is not None:
            self.set_next(nxt)
        self.previous = None
        if previous is not None:
            self.set_previous(previous)

    def set_next(self, nxt: "JourneyLocation"):
        nxt.previous = self
        self.next = nxt

    def set_previous(self, previous: "JourneyLocation"):
        previous.next = self
        self.previous = previous


class Journey:
    def __init__(self, locations: List[Location]):
        self.locations = []
        self.legs = []
        for location in locations:
            self.append(location)

    def insert(self, index: int, location: Location):
        self.locations.insert(index=index, object=location)

    def append(self, location: Location):
        self.locations.append(location)
