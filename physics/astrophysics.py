"""
A module for handling astronomical objects, including star systems and their subordinate systems and objects.

This has a hierarchical structure: the StarList is the overarching object, and contains a list of StarSystems; a
StarSystem contains a list of stars within that system; a Star contains a list of planets orbiting it; and a Planet
contains a list of Moons. The StarList also contains lists of all the stars, planets and moons that are within its
star_systems, to keep better track.
Within each class of object, some of its traits can be calculated. For example, a star's main sequence luminosity may
be calculated from its mass using star.ms_luminosity().
"""

import numpy as np
import numpy.random as r
import math
import physics.units as u
import physics.maths as ma
import matplotlib.pyplot as plt
import pandas as pd
import sys
# This SAYS it is unused, but it isn't. Do not delete.
from mpl_toolkits.mplot3d import Axes3D


# from queue import PriorityQueue


# Possible model for distribution of moons: standard deviation (of sma) proportional to mass of host planet
# OR: max orbit at 1/2 Hill Sphere distance, or std dev at 1/4 Hill Sphere


# TODO: random planet/moon generator
# TODO: radius-mass relation
# TODO: Nightsky projection
# TODO: generate solar system
# TODO: Titius-Bode Law

# TODO: Example scripts
# TODO: Method for reading in exoplanet catalogue. Try to match names, alternate names, then ra & dec

class StarList:
    """
    A StarList is an object containing a list of StarSystems, Stars, Planets and Moons, with methods for doing things
    with them.
    """

    def __init__(self):
        self.star_sys_list = list()
        self.star_list = list()
        self.planet_list = list()
        self.moon_list = list()

    def __getitem__(self, item):
        return self.star_list[item]

    def __str__(self):
        return str(len(self.star_sys_list)) + " Star Systems, " + str(len(self.star_list)) + " Stars, " + str(
            len(self.planet_list)) + " Planets, " + str(len(self.moon_list)) + " Moons"

    def size(self):
        """
        :return: tuple[4] of sizes, [star_sys_list, star_list, planet_list, moon_list]
        """

        return len(self.star_sys_list), len(self.star_list), len(self.planet_list), len(self.moon_list)

    def add_star_system(self, syst: "StarSystem"):
        """
        Add a StarSystem to the StarList.
        :param syst: StarSystem: the item to be added.
        """
        if type(syst) is StarSystem:
            self.star_sys_list.append(syst)
        else:
            raise ValueError('Must be of StarSystem class')

    def add_star(self, star: "Star"):
        """
        Add a Star to the StarList, and all subsidiary planets (and moons)
        :param star: Star: the item to be added.
        """
        if type(star) is Star:
            self.star_list.append(star)
            for p in star.planets:
                if p not in self.planet_list:
                    self.add_planet(p)
        else:
            raise ValueError('Must be of Star class')

    def add_planet(self, planet: "Planet"):
        """
        Add a Planet to the StarList, and all subsidiary moons.
        :param planet: Planet: The item to be added.
        :return:
        """
        if type(planet) is Planet:
            self.planet_list.append(planet)
            for m in planet.moons:
                if m not in self.moon_list:
                    self.add_moon(m)
        else:
            raise ValueError('Must be of Planet class')

    def add_moon(self, moon: "Moon"):
        """
        Add a Moon to the StarList.
        :param moon: The item to be added.
        :return:
        """
        if type(moon) is Moon:
            self.moon_list.append(moon)
        else:
            raise ValueError('Must be of Moon class')

    def get_system(self, idn: "StarSystem", create: "bool" = False):
        """
        Searches for and returns a system with the specified idn in star_sys_list. If the system is not found, one of 
        two cases: if create is False, None is returned; if create is True, a new system with that idn is made.
        :param idn: int: idn of desired StarSystem.
        :param create: bool: Determines if a new System is created (True), if the specified idn is not found.
        :return: StarSystem: searched StarSystem or None
        """
        for syst in self.star_sys_list:
            if syst.idn == idn:
                return syst
        else:
            syst = None
            if create:
                syst = StarSystem()
                syst.idn = idn
                self.add_star_system(syst)

            return syst

    def get_star(self, idn: "int", create: "bool" = False):
        """
        Searches for and returns a Star with the specified idn in star_list. If the Star is not found, one of two cases:
        if create is False, None is returned; if create is True, a new Star with that idn is made.
        :param idn: int: idn of desired Star.
        :param create: bool: Determines if a new Star is created (True), if the specified idn is not found.
        :return: Star: searched Star or None
        """

        for star in self.star_list:
            if star.idn == idn:
                return star
        else:
            star = None
            if create:
                star = Star()
                star.idn = idn
                self.add_star(star)

            return star

    def get_planet(self, idn: "int", create: "bool" = False):
        """
        Searches for and returns a Planet with the specified idn in planet_list. If the Planet is not found, one of two 
        cases: if create is False, None is returned; if create is True, a new Planet with that idn is made.
        :param idn: int: idn of desired Planet.
        :param create: bool: Determines if a new Planet is created (True), if the specified idn is not found.
        :return: Planet: searched Planet or None
        """

        for planet in self.planet_list:
            if planet.idn == idn:
                return planet
        else:
            planet = None
            if create:
                planet = Planet()
                planet.idn = idn
                self.add_planet(planet)

            return planet

    def get_moon(self, idn: 'int', create: 'bool' = False):
        """
        Searches for and returns a Moon with the specified idn in moon_list. If the Moon is not found, one of two
        cases: if create is False, None is returned; if create is True, a new Moon with that idn is made.
        :param idn: int: idn of desired Moon.
        :param create: bool: Determines if a new Moon is created (True), if the specified idn is not found.
        :return: Moon: searched Moon or None
        """

        for moon in self.moon_list:
            if moon.idn == idn:
                return moon
        else:
            moon = None
            if create:
                moon = Moon()
                moon.idn = idn
                self.add_moon(moon)

            return moon

    def furthest_star(self):
        # TODO: Add ability to specify point to measure distance from, with 0,0,0 as default
		"""
        :return: StarSystem in the list with the greatest distance (from origin)
        """
        maxim = 0.
        furthest = None
        for s in self.star_list:
            if s.distance > maxim:
                maxim = s.distance
                furthest = s

        return furthest

    def find_unvisited(self):
        """
        :return: StarSystem: the first member of star_list that has visited set to False.
        """
        for s in self.star_list:
            if not s.visited:
                return s

        return None

    def find_nearest_neighbour(self, s: "Star"):
        """
        Finds the nearest spatial neighbour of the parameter star and sets s.nearest_neighbour to that; also sets
        s.nearest_neighbour_d to the distance between them.
        :param s: Star: The StarSystem of which you wish to find the nearest neighbour.
        :return: Star: The nearest neighbour of s.
        """
        if type(s) is Star:
            # minim is the smallest known distance to a star.
            minim = sys.float_info.max
            # nrst is the closest known star.
            # We find unvisited because in the creep algorithms for spaceflight we only want to find unvisited.
            nrst = self.find_unvisited()

            for other in self.star_list:
                if other is not s:
                    d = s.distance_to(other)

                    if d < minim:
                        minim = d
                        nrst = other

            s.set_nearest_neighbour(nrst)
            s.nearest_neighbour_d = minim

            return nrst, minim

        else:
            raise ValueError('Must be of StarSystem class')

    def find_unvisited_neighbour(self, s: "Star"):
        """
        Finds the nearest spatial neighbour of the parameter star that has not been visited; also marks that the found
        star as visited.
        :param s: StarSystem: The StarSystem of which you wish to find the nearest neighbour.
        :return: (StarSystem, float): The nearest neighbour of ss with visited set to False; the distance to that
        StarSystem.
        """
        if type(s) is Star:

            minim = sys.float_info.max
            nrst = self.find_unvisited()
            if nrst is not None:
                nrst.visited = True
            for other in self.star_list:
                if other is not s and not other.visited:
                    d = s.distance_to(other)

                    if d < minim:
                        minim = d
                        nrst = other

            return nrst, minim

        else:
            raise ValueError('Must be of StarSystem class')

    def all_nearest_neighbours(self):
        """
        All Stars in the list will have find_nearest_neighbour called on them.
        """
        for s in self.star_list:
            self.find_nearest_neighbour(s)

    def plot_stars(self, bl: "bool" = True, suppress: "bool" = False):
        """
        Plots the positions of all stars in a three-dimensional plot, with black marks. Plots visited stars in red.
        :param bl: bool: If True, for each star, draws a black line along the x-y plane to the star's x-y position, and
        another black line from the end of that line to the star. This helps understand the star's position visually.
        :param suppress: bool: If False, plots the figure.
        :return: matplotlib.pyplot.figure: The three-dimensional figure, can be plotted with
        matplotlib.pyplot.show(star_map)
        """
        star_map = plt.figure()
        # Set 3d projection
        ax = star_map.add_subplot(111, projection='3d')
        for i in self.star_list:
            print("Plotting " + str(i.idn) + ": " + i.name)
            # Plot stars
            if i.visited:
                colour = 'red'
            else:
                colour = 'black'
            ax.scatter(xs=i.x, ys=i.y, zs=i.z, c=colour)
            if bl:
                # Draw lines to stars
                ax.plot(xs=[i.x, i.x], ys=[i.y, i.y], zs=[i.z, 0], c='black')
                ax.plot(xs=[i.x, 0], ys=[i.y, 0], zs=[0, 0], c='black')

        if not suppress:
            plt.show(star_map)
        return star_map

    def plot_empires(self, stars: "list", extents: "list", others: "bool" = True):
        """
        Plots the stars belonging to an empire or empires. That is, for each star[i], it plots the stars within
        extents[i] of that star with a unique colour. Also prints the number of stars in each empire.
        :param stars: List containing the central stars of each empire.
        :param extents: Iterable containing the extent each empire reaches, in light years.
        :param others: Determines if Stars that are not a part of the "empires" are plotted - they are if True.
        :return: matplotlib.pyplot.figure: the figure on which all of this is plotted.
        """
        if type(stars) is list:

            star_plot = plt.figure()
            ax = star_plot.add_subplot(111, projection='3d')
            # List of colours to pick from.
            colours = ["purple", "red", "blue", "green", "yellow", "cyan", "orange", "violet", "pink", "brown", "gray",
                       "indigo"]

            handles = []
            handle = 0
            labels = list()
            count_strings = []

            for i, capital in enumerate(stars):
                if type(capital) is not Star:
                    raise ValueError("stars must be list of Stars")
                else:
                    count = 0
                    labels.append(capital.name)
                    for j, s in enumerate(self.star_list):
                        if s.distance_to(capital) < extents[i]:
                            count += 1
                            print("Plotting " + str(j) + ": " + s.name)
                            handle = ax.scatter(xs=s.x, ys=s.y, zs=s.z, c=colours[i], s=9)

                            s.visited = True

                    count_strings.append(str(i) + ". " + capital.name + ": " + str(count) + " Stars")
                    handles.append(handle)

            # Plot stars not in the empires in black
            if others:
                for j, s in enumerate(self.star_list):
                    if not s.visited:
                        print("Plotting " + str(j) + ": " + s.name)
                        ax.scatter(xs=s.x, ys=s.y, zs=s.z, c="black", s=9)

            star_plot.legend(handles, labels, 'upper right')

            self.reset_visits()
            for i in count_strings:
                print(i)
            print("Rendering")
            plt.show(star_plot)
            return star_plot

        else:
            raise ValueError("empires must be list of StarSystem")

    def find_star(self, name: "str"):
        """
        :param name: str: Name of desired Star. Must be spelt exactly correct.
        :return: Star: If the Star exists in list, returns that; None if it does not.
        """
        if type(name) is str:

            for s in self.star_list:
                if s.name == name:
                    return s

            return None

        else:
            raise ValueError("Name must be a string")

    def form_subset(self, num=100):
        """
        Returns a StarList containing only the first num StarSystems in this StarList. Recommend sorting the
        star_system_list by desired trait before using.
        :param num:
        :return:
        """
        if num < len(self.star_list) and type(num) == int:

            new_list = StarList()
            for i in self.star_list[:num]:
                new_list.add_star(i)

            return new_list

        else:
            raise ValueError("Num must be an int smaller than the size of the orginal")

    def limit_by_distance(self, limit):
        """Returns a StarList containing only stars whose distance is less than the limit."""
        new_list = StarList()
        for s in self.star_list:
            if s.distance < limit:
                new_list.add_star(s)

        return new_list

    def reset_visits(self):
        """
        Sets the 'visited' field in each star to False. I recommend using this after running any code that uses
        'visited.'
        """
        for s in self:
            s.visited = False

    def clear_political(self):
        for star in self.star_list:
            star.political = ""

    def clear_explored(self):
        for star in self:
            star.year_explored = None

    def read_systems_xl(self, path: "str" = "SF_Cat_StarSystems"):
        """
        Reads in StarSystems from a properly-formatted .xlsx file. For example of proper formatting, see included
        format files.
        :param path: Location or relative location of file.
        :return:
        """

        i = len(path)
        if path[i - 5:] != ".xlsx":
            path += ".xlsx"
        print("Reading StarSystems XL")
        self.star_list.sort(key=lambda s: s.idn)
        cat = pd.read_excel(path)
        cat = cat.as_matrix()
        print("Star Systems XL Imported")

        for row in cat:
            syst = StarSystem()
            syst.idn = int(row[0])
            syst.name = str(row[1])

            syst.star_str = str(row[2])
            j = 0
            for i, char in enumerate(syst.star_str):
                if char == ';':
                    ind = int(syst.star_str[j:i])
                    star = self.get_star(ind)
                    if star is not None:
                        syst.add_star(star)
                    j = i + 2

            self.add_star_system(syst)

            print("Imported " + str(syst.idn) + ": " + syst.name)

    def read_stars_xl(self, path: "str" = "SF_Cat_"):
        i = len(path)
        if path[i - 5:] != ".xlsx":
            path += ".xlsx"

        print("Reading Stars XL")
        self.planet_list.sort(key=lambda pl: pl.idn)

        cat = pd.read_excel(path)
        print("Stars XL Imported")
        cat = cat.as_matrix()
        for row in cat:
            star = Star()
            star.idn = int(row[0])
            star.name = str(row[1])
            if star.name == "nan":
                star.name = ""
            star.mass = float(row[2])
            star.hip = str(row[3])
            if star.hip == "nan":
                star.hip = ""
            star.hd = str(row[4])
            if star.hd == "nan":
                star.hd = ""
            star.hr = str(row[5])
            if star.hr == "nan":
                star.hr = ""
            star.gl = str(row[6])
            if star.gl == "nan":
                star.gl = ""
            star.bf = str(row[7])
            if star.bf == "nan":
                star.bf = ""
            star.proper = str(row[8])
            if star.proper == "nan":
                star.proper = ""
            star.asc = float(row[9])
            star.dec = float(row[10])
            star.distance = float(row[11])
            star.pmra = float(row[12])
            star.pmdec = float(row[13])
            star.rv = float(row[14])
            star.mag = float(row[15])
            star.abs_mag = float(row[16])
            star.spec_type = str(row[17])
            if star.spec_type == "nan":
                star.spec_type = ""
            star.ci = str(row[18])
            if star.ci == "nan":
                star.ci = ""
            star.x = float(row[19])
            star.y = float(row[20])
            star.z = float(row[21])
            star.vx = float(row[22])
            star.vy = float(row[23])
            star.vz = float(row[24])
            star.rarad = float(row[25])
            star.decrad = float(row[26])
            star.pmrarad = float(row[27])
            star.pmdecrad = float(row[28])
            star.bayer = str(row[29])
            if star.bayer == "nan":
                star.bayer = ""
            star.flam = str(row[30])
            if star.flam == "nan":
                star.flam = ""
            star.con = str(row[31])
            if star.con == "nan":
                star.con = ""
            star.luminosity = float(row[32])
            star.var = str(row[33])
            if star.var == "nan":
                star.var = ""
            star.var_min = float(row[34])
            star.var_max = float(row[35])
            star.tau_ms = float(row[36])
            star.hz_inner = float(row[37])
            star.hz_outer = float(row[38])
            star.political = str(row[39])
            if star.political == "nan":
                star.political = ""
            star.year_explored = float(row[40])
            star.local_id = int(row[41])
            star.system_id = int(row[42])
            star.system_name = str(row[43])
            if star.system_name == "nan":
                star.system_name = ""

            star.planet_str = str(row[44])
            if star.planet_str == "nan":
                star.planet_str = ""
            j = 0
            for i, char in enumerate(star.planet_str):
                if char == ';':
                    ind = int(star.planet_str[j:i])
                    planet = self.get_planet(ind)
                    if planet is not None:
                        star.add_planet(planet)
                    j = i + 2

            # star.wormholes_to = str(row[45])
            if star.wormholes_to == "nan":
                star.wormholes_to = ""

            self.add_star(star)

            print("Imported " + str(star.idn) + ": " + star.name)

    def read_planets_xl(self, path: "str" = "SF_Cat_Planets"):
        i = len(path)
        if path[i - 5:] != ".xlsx":
            path += ".xlsx"
        print("Reading Planets XL")
        cat = pd.read_excel(path)
        print("Planets XL Imported")
        cat = cat.as_matrix()
        self.moon_list.sort(key=lambda moon: moon.idn)

        for row in cat:
            planet = Planet()
            planet.idn = int(row[0])
            planet.name = str(row[1])
            if planet.name == "nan":
                planet.name = ""
            planet.type = str(row[2])
            if planet.type == "nan":
                planet.type = ""
            planet.mass = float(row[3])
            planet.radius = float(row[4])
            planet.g = float(row[5])
            planet.period = float(row[6])
            planet.rot_period = float(row[7])
            planet.sma = float(row[8])
            planet.political = str(row[9])
            if planet.political == "nan":
                planet.political = ""
            planet.star_name = str(row[10])
            if planet.star_name == "nan":
                planet.star_name = ""
            planet.star_id = int(row[11])
            planet.local_id = int(row[12])

            planet.moon_str = str(row[13])
            j = 0
            for i, char in enumerate(planet.moon_str):
                if char == ';':
                    ind = int(planet.moon_str[j:i])
                    moon = self.get_moon(ind)
                    if moon is not None:
                        planet.add_moon(moon)
                    j = i + 2

            print("Imported " + str(planet.idn) + ": " + planet.name)

            self.add_planet(planet)

    def read_moons_xl(self,
                      path: "str" = "SF_Cat_Moons"):
        i = len(path)
        if path[i - 5:] != ".xlsx":
            path += ".xlsx"
        print("Reading direct XL")
        cat = pd.read_excel(path)
        print("direct XL Imported")
        cat = cat.as_matrix()
        for row in cat:
            moon = Moon()
            moon.idn = int(row[0])
            moon.name = str(row[1])
            if moon.name == "nan":
                moon.name = ""
            moon.mass = float(row[2])
            moon.radius = float(row[3])
            moon.g = float(row[4])
            moon.sma = float(row[5])
            moon.period = float(row[6])
            moon.planet_name = str(row[7])
            if moon.planet_name == "nan":
                moon.planet_name = ""
            moon.planet_id = int(row[8])
            moon.id_local = int(row[9])
            moon.political = str(row[10])
            if moon.political == "nan":
                moon.political = ""

            print("Imported " + str(moon.idn) + ": " + moon.name)

            self.add_moon(moon)

        print("On Read: " + str(len(self.moon_list)))

    def read_all_xl(self, moon_path: "str" = "SF_Cat_Moons", planet_path: "str" = "SF_Cat_Planets",
                    star_path: "str" = "SF_Cat_Stars", syst_path: "str" = "SF_Cat_StarSystems"):

        self.read_moons_xl(moon_path)
        self.read_planets_xl(planet_path)
        self.read_stars_xl(star_path)
        self.read_systems_xl(syst_path)

    def read_systems(self, path: "str" = "SF_Cat_StarSystems"):
        """
        Reads in StarSystems from a properly-formatted .csv file. For example of proper formatting, see included
        format files.
        :param path: Location or relative location of file.
        :return:
        """

        i = len(path)
        if path[i - 4:] != ".csv":
            path += ".csv"
        print("Reading StarSystems CSV")
        self.star_list.sort(key=lambda s: s.idn)
        cat = pd.read_csv(path)
        cat = cat.as_matrix()
        print("Star Systems CSV Imported")

        for row in cat:
            syst = StarSystem()
            syst.idn = int(row[1])
            syst.name = str(row[2])

            syst.star_str = str(row[3])
            j = 0
            for i, char in enumerate(syst.star_str):
                if char == ';':
                    ind = int(syst.star_str[j:i])
                    star = self.get_star(ind)
                    if star is not None:
                        syst.add_star(star)
                    j = i + 2

            self.add_star_system(syst)

            print("Imported " + str(syst.idn) + ": " + syst.name)

    def read_stars(self, path: "str" = "SF_Cat_"):
        i = len(path)
        if path[i - 4:] != ".csv":
            path += ".csv"

        print("Reading Stars CSV")
        self.planet_list.sort(key=lambda pl: pl.idn)

        cat = pd.read_csv(path)
        print("Stars CSV Imported")
        cat = cat.as_matrix()

        for row in cat:
            star = Star()
            star.idn = int(row[1])
            star.name = str(row[2])
            if star.name == "nan":
                star.name = ""
            star.mass = float(row[3])
            star.hip = str(row[4])
            if star.hip == "nan":
                star.hip = None
            else:
                star.hip = math.floor(float(star.hip))
            star.hd = str(row[5])
            if star.hd == "nan":
                star.hd = ""
            else:
                star.hd = math.floor(float(star.hd))
            star.hr = str(row[6])
            if star.hr == "nan":
                star.hr = ""
            else:
                star.hr = math.floor(float(star.hr))
            star.gl = str(row[7])
            if star.gl == "nan":
                star.gl = ""
            star.bf = str(row[8])
            if star.bf == "nan":
                star.bf = ""
            star.proper = str(row[9])
            if star.proper == "nan":
                star.proper = ""
            star.asc = float(row[10])
            star.dec = float(row[11])
            star.distance = float(row[12])
            star.pmra = float(row[13])
            star.pmdec = float(row[14])
            star.rv = float(row[15])
            star.mag = float(row[16])
            star.abs_mag = float(row[17])
            star.spec_type = str(row[18])
            if star.spec_type == "nan":
                star.spec_type = ""
            star.ci = float(row[19])
            star.x = float(row[20])
            star.y = float(row[21])
            star.z = float(row[22])
            star.vx = float(row[23])
            star.vy = float(row[24])
            star.vz = float(row[25])
            star.rarad = float(row[26])
            star.decrad = float(row[27])
            star.pmrarad = float(row[28])
            star.pmdecrad = float(row[29])
            star.bayer = str(row[30])
            if star.bayer == "nan":
                star.bayer = ""
            star.flam = str(row[31])
            if star.flam == "nan":
                star.flam = ""
            star.con = str(row[32])
            if star.con == "nan":
                star.con = ""
            star.luminosity = float(row[33])
            star.var = str(row[34])
            if star.var == "nan":
                star.var = ""
            star.var_min = float(row[35])
            star.var_max = float(row[36])
            star.tau_ms = float(row[37])
            star.hz_inner = float(row[38])
            star.hz_outer = float(row[39])
            star.political = str(row[40])
            if star.political == "nan":
                star.political = ""
            star.year_explored = float(row[41])
            star.local_id = int(row[42])
            star.system_id = int(row[43])
            star.system_name = str(row[44])
            if star.system_name == "nan":
                star.system_name = ""

            star.planet_str = str(row[45])
            if star.planet_str == "nan":
                star.planet_str = ""
            j = 0
            for i, char in enumerate(star.planet_str):
                if char == ';':
                    ind = int(star.planet_str[j:i])
                    planet = self.get_planet(ind)
                    if planet is not None:
                        star.add_planet(planet)
                    j = i + 2

            # star.wormholes_to = str(row[45])
            if star.wormholes_to == "nan":
                star.wormholes_to = ""

            self.add_star(star)

            print("Imported " + str(star.idn) + ": " + star.name)

    def read_planets(self, path: "str" = "SF_Cat_Planets"):
        i = len(path)
        if path[i - 4:] != ".csv":
            path += ".csv"
        print("Reading Planets CSV")
        cat = pd.read_csv(path)
        print("Planets CSV Imported")
        cat = cat.as_matrix()
        self.moon_list.sort(key=lambda moon: moon.idn)

        for row in cat:
            planet = Planet()
            planet.idn = int(row[1])
            planet.name = str(row[2])
            if planet.name == "nan":
                planet.name = ""
            planet.type = str(row[3])
            if planet.type == "nan":
                planet.type = ""
            planet.mass = float(row[4])
            planet.radius = float(row[5])
            planet.g = float(row[6])
            planet.period = float(row[7])
            planet.rot_period = float(row[8])
            planet.sma = float(row[9])
            planet.political = str(row[10])
            if planet.political == "nan":
                planet.political = ""
            planet.star_name = str(row[11])
            if planet.star_name == "nan":
                planet.star_name = ""
            planet.star_id = int(row[12])
            planet.local_id = int(row[13])

            planet.moon_str = str(row[14])
            j = 0
            for i, char in enumerate(planet.moon_str):
                if char == ';':
                    ind = int(planet.moon_str[j:i])
                    moon = self.get_moon(ind)
                    if moon is not None:
                        planet.add_moon(moon)
                    j = i + 2

            print("Imported " + str(planet.idn) + ": " + planet.name)

            self.add_planet(planet)

    def read_moons(self, path: "str" = "SF_Cat_Moons"):
        i = len(path)
        if path[i - 4:] != ".csv":
            path += ".csv"
        print("Reading direct CSV")
        cat = pd.read_csv(path)
        print("direct CSV Imported")
        cat = cat.as_matrix()
        for row in cat:
            moon = Moon()
            moon.idn = int(row[1])
            moon.name = str(row[2])
            if moon.name == "nan":
                moon.name = ""
            moon.mass = float(row[3])
            moon.radius = float(row[4])
            moon.g = float(row[5])
            moon.sma = float(row[6])
            moon.period = float(row[7])
            moon.planet_name = str(row[8])
            if moon.planet_name == "nan":
                moon.planet_name = ""
            moon.planet_id = int(row[9])
            moon.id_local = int(row[10])
            moon.political = str(row[11])
            if moon.political == "nan":
                moon.political = ""

            print("Imported " + str(moon.idn) + ": " + moon.name)

            self.add_moon(moon)

    def read_all(self, moon_path: "str" = "SF_Cat_Moons", planet_path: "str" = "SF_Cat_Planets",
                 star_path: "str" = "SF_Cat_Stars", syst_path: "str" = "SF_Cat_StarSystems"):

        self.read_moons(moon_path)
        self.read_planets(planet_path)
        self.read_stars(star_path)
        self.read_systems(syst_path)

    def read_all_short(self, path, ver):
        self.read_all(path + "SF_Cat_Moons_" + ver, path + "SF_Cat_Planets_" + ver, path + "SF_Cat_Stars_" + ver,
                      path + "SF_Cat_StarSystems_" + ver)

    def read_hyg(self,
                 path: "str" = "C:\\Users\\Lachlan\\Google Drive\\Projects\\Python\\physics\\astronomy\\hygdata_LM.xlsx"):
        """
        Imports the StarList from a (properly formatted) .xlsx file version of HYG database.
        :param path: str:
        :return:
        """
        cat = pd.read_excel(path)
        print("XL Imported")
        cat = cat.as_matrix()
        print("As matrix completed")

        for row in cat:

            star = Star()

            # Copy columns first

            star.idn = int(row[0])
            star.hip = str(row[1])
            star.hd = str(row[2])
            star.hr = str(row[3])
            star.gl = str(row[4])
            star.bf = str(row[5])
            star.proper = str(row[6])
            star.asc = float(row[7])
            star.dec = float(row[8])
            star.distance = u.length_to_length(row[9], 'pc', 'ly')
            star.pmra = float(row[10])
            star.pmdec = float(row[11])
            star.rv = float(row[12])
            star.mag = float(row[13])
            star.abs_mag = float(row[14])
            star.spec_type = str(row[15])
            star.ci = float(row[16])
            star.x = u.length_to_length(float(row[17]), 'pc', 'ly')
            star.y = u.length_to_length(float(row[18]), 'pc', 'ly')
            star.z = u.length_to_length(float(row[19]), 'pc', 'ly')
            star.vx = u.length_to_length(float(row[20]), 'pc', 'ly')
            star.vy = u.length_to_length(float(row[21]), 'pc', 'ly')
            star.vz = u.length_to_length(float(row[22]), 'pc', 'ly')
            star.rarad = float(row[23])
            star.decrad = float(row[24])
            star.pmrarad = float(row[25])
            star.pmdecrad = float(row[26])
            star.bayer = str(row[27])
            star.flam = str(row[28])
            star.con = str(row[29])
            star.local_id = int(row[30])
            star.system_id = int(row[31])
            star.system_name = str(row[32])
            star.luminosity = float(row[33])
            star.var = str(row[34])
            star.var_min = float(row[35])
            star.var_max = float(row[36])

            # Pick a name for the star from the selection given, with priority from right to left.
            if star.proper == "nan":
                if star.bf == "nan":
                    if star.gl == "nan":
                        if star.hr == "nan":
                            if star.hd == "nan":
                                if star.hip == "nan":
                                    name = str(star.idn)
                                else:
                                    name = "HIP " + str(star.hip)
                            else:
                                name = "HD " + str(star.hd)
                        else:
                            name = "HR " + str(star.hr)
                    else:
                        name = star.gl
                else:
                    name = star.bf
            else:
                name = star.proper

            star.name = name

            # Set up a star system around it, or else find the system it belongs to.
            star_sys = self.get_system(star.system_id, create=True)

            print("Imported " + str(star.idn) + ": " + star.name)

            # If no system name is specified, take the name of the primary.

            if star_sys.name in [None, 'None', "nan", ""]:

                if star.system_name not in [None, 'None', "nan", ""]:

                    star_sys.name = star.system_name

                else:
                    if star.local_id == 1:
                        star_sys.name = star.name + " System"

            for s in star_sys:
                s.system_name = star_sys.name

            star_sys.add_star(star)
            self.add_star(star)

    def read_eu_exoplanet(self, path):

        cat = pd.read_csv(path)
        cat = cat.as_matrix()

        for row in cat:
            name = str(row[68])
            star = self.find_star(name)
            if star is None:
                star = Star()

                star.name = str(row[68])
                star.asc = float(row[69])
                star.dec = float(row[70])
                star.mag = float(row[71])
                star.distance = float(row[76])
                star.metallicity = float(row[79])
                star.radius = float(row[85])
                star.spec_type = str(row[88])
                star.age = float(row[89]) * 1e9
                star.temp_eff = float(row[92])

                name_str = str(row[97])

                if "HIP " in name_str:
                    hip = name_str[name_str.find("HIP") + 4:]
                    end = hip.find(",")
                    if end == -1:
                        end = len(hip)
                    hip = hip[:end]
                    star.hip = hip
                if "GL " in name_str:
                    gl = name_str[name_str.find("GL") + 3:]
                    end = gl.find(",")
                    if end == -1:
                        end = len(gl)
                    gl = gl[:end]
                    star.gl = "Gl " + gl
                if "Gliese " in name_str:
                    gl = name_str[name_str.find("Gliese") + 7:]
                    end = gl.find(",")
                    if end == -1:
                        end = len(gl)
                    gl = gl[:end]
                    star.gl = "Gl " + gl
                if "GJ " in name_str:
                    gj = name_str[name_str.find("GJ") + 3:]
                    end = gj.find(",")
                    if end == -1:
                        end = len(gj)
                    gj = gj[:end]
                    star.gl = "GJ " + gj
                if "HD " in name_str:
                    hd = name_str[name_str.find("HD") + 3:]
                    end = hd.find(",")
                    if end == -1:
                        end = len(hd)
                    hd = hd[:end]
                    star.hd = hd
                if "HR " in name_str:
                    hr = name_str[name_str.find("HR") + 3:]
                    end = hr.find(",")
                    if end == -1:
                        end = len(hr)
                    hr = hr[:end]
                    star.hr = hr
                if "WISE " in name_str:
                    wise = name_str[name_str.find("WISE") + 3:]
                    end = wise.find(",")
                    if end == -1:
                        end = len(wise)
                    wise = wise[:end]
                    star.wise = wise
                if "WISEP " in name_str:
                    wisep = name_str[name_str.find("WISEP") + 6:]
                    end = wisep.find(",")
                    if end == -1:
                        end = len(wisep)
                    wisep = wisep[:end]
                    star.wisep = wisep
                if "WISEPC " in name_str:
                    wisepc = name_str[name_str.find("WISEPC") + 7:]
                    end = wisepc.find(",")
                    if end == -1:
                        end = len(wisepc)
                    wisepc = wisepc[:end]
                    star.wisepc = wisepc
                if "2MASS " in name_str:
                    two_mass = name_str[name_str.find("2MASS") + 6:]
                    end = two_mass.find(",")
                    if end == -1:
                        end = len(two_mass)
                    two_mass = two_mass[:end]
                    star.two_mass = two_mass
                if "SDSS " in name_str:
                    sdss = name_str[name_str.find("SDSS") + 5:]
                    end = sdss.find(",")
                    if end == -1:
                        end = len(sdss)
                    sdss = sdss[:end]
                    star.sdss = sdss
                if "EPIC " in name_str:
                    epic = name_str[name_str.find("EPIC") + 5:]
                    end = epic.find(",")
                    if end == -1:
                        end = len(epic)
                    epic = epic[:end]
                    star.epic = epic
                if "SAO " in name_str:
                    sao = name_str[name_str.find("SAO") + 4:]
                    end = sao.find(",")
                    if end == -1:
                        end = len(sao)
                    sao = sao[:end]
                    star.sao = sao

                name_str = str(row[97])
                if name_str not in ["", None, "nan"]:
                    end = False
                    while not end:
                        last = name_str.find(",")
                        if last == -1:
                            last = len(name_str)
                            end = True
                        star.names.append(name_str[:last])
                        name_str = name_str[last + 2:]

                self.add_star(star)

            planet = Planet()

            planet.name = str(row[0])
            planet.mass = u.mass_to_mass(float(row[2]), frm="M_J", to="M_E")
            planet.radius = float(row[8])
            planet.period = float(row[11])
            planet.sma = float(row[14])
            planet.eccentricity = float(row[17])
            planet.inclination = float(row[20])
            planet.discovered = float(row[24])
            planet.omega = float(row[26])
            planet.semi_amplitude = float(row[50])

            temp_calc = float(row[53])
            temp_measure = float(row[56])
            if temp_calc in ["nan", "", None]:
                planet.temp = temp_measure
            else:
                planet.temp = temp_calc

            planet.geometric_albedo = float(row[58])
            planet.detection = str(row[63])
            planet.mass_det_type = str(row[64])
            planet.rad_det_type = str(row[65])

            name_str = str(row[66])
            if name_str not in ["", None, "nan"]:
                end = False
                while not end:
                    last = name_str.find(",")
                    if last == -1:
                        last = len(name_str)
                        end = True
                    planet.names.append(name_str[:last])
                    name_str = name_str[last + 2:]

            star.add_planet(planet)
            print(str(planet.name) + " Imported")

    def merge_lists(self, other: "StarList"):

        for star in other:
            star.match_star(self)



    def write_systems_xl(self, path: "str" = "SF_Cat_StarSystems"):
        """
        :param path: Name to which you wish to save the file.
        :return:
        """

        i = len(path)
        if path[i - 5:] != ".xlsx":
            path += ".xlsx"
        self.star_sys_list.sort(key=lambda syst: syst.idn)

        ids = []
        name = []
        stars = []

        for syst in self.star_sys_list:
            print("Writing " + str(syst.idn) + ": " + syst.name)
            ids.append(syst.idn)
            name.append(syst.name)

            # The 'if' statement ensures that we don't wipe out the stars if they haven't been read in.
            if len(syst.stars) > 0:
                syst.star_str = ""
                for star in syst.stars:
                    syst.star_str += str(star.idn) + "; "
            stars.append(syst.star_str)

        output = pd.DataFrame({"00 ID": ids, "01 Name": name, "02 Stars": stars})
        print("Writing StarSystem XL")
        output.to_excel(path)

    def write_stars_xl(self, path: "str" = "SF_Cat_Stars", sort=lambda star: star.idn):

        i = len(path)
        if path[i - 5:] != ".xlsx":
            path += ".xlsx"

        self.star_list.sort(key=sort)

        ids = []
        name = []
        mass = []

        hip = []
        hd = []
        hr = []
        gl = []
        bf = []
        proper = []
        asc = []
        dec = []
        distance = []
        pmra = []
        pmdec = []
        rv = []
        mag = []
        abs_mag = []
        spect = []
        ci = []
        x = []
        y = []
        z = []
        vx = []
        vy = []
        vz = []
        rarad = []
        decrad = []
        pmrarad = []
        pmdecrad = []
        bayer = []
        flam = []
        con = []
        luminosity = []
        var = []
        var_min = []
        var_max = []

        tau_ms = []
        hz_inner = []
        hz_outer = []
        political = []
        year_explored = []
        local_id = []
        system_id = []
        system_name = []
        planets = []
        wormholes_to = []

        for star in self.star_list:
            print("Writing " + str(star.idn) + ": " + star.name)
            ids.append(star.idn)
            mass.append(star.mass)
            name.append(star.name)

            hip.append(star.hip)
            hd.append(star.hd)
            hr.append(star.hr)
            gl.append(star.gl)
            bf.append(star.bf)
            proper.append(star.proper)
            asc.append(star.asc)
            dec.append(star.dec)
            distance.append(star.distance)
            pmra.append(star.pmra)
            pmdec.append(star.pmdec)
            rv.append(star.rv)
            mag.append(star.mag)
            abs_mag.append(star.abs_mag)
            spect.append(star.spec_type)
            ci.append(star.ci)
            x.append(star.x)
            y.append(star.y)
            z.append(star.z)
            vx.append(star.x)
            vy.append(star.y)
            vz.append(star.z)
            rarad.append(star.rarad)
            decrad.append(star.decrad)
            pmrarad.append(star.pmrarad)
            pmdecrad.append(star.pmdecrad)
            bayer.append(star.bayer)
            flam.append(star.flam)
            con.append(star.con)
            luminosity.append(star.luminosity)
            var.append(star.var)
            var_min.append(star.var_min)
            var_max.append(star.var_max)

            tau_ms.append(star.tau_ms)
            hz_inner.append(star.hz_inner)
            hz_outer.append(star.hz_outer)
            political.append(star.political)
            year_explored.append(star.year_explored)

            local_id.append(star.local_id)
            system_id.append(star.system_id)
            system_name.append(star.system_name)

            # The 'if' statement ensures that we don't wipe out the planets if they haven't been read in.
            if len(star.planets) > 0:
                star.planet_str = ""
                for planet in star.planets:
                    star.planet_str += str(planet.idn) + "; "
            planets.append(star.planet_str)
            wormholes_to.append(star.wormholes_to)

        output = pd.DataFrame(
            {"00 ID": ids, "01 Name": name, "02 Mass": mass, "03 HIP ID": hip, "04 HD ID": hd, "05 HR ID": hr,
             "06 GL ID": gl, "07 BF ID": bf, "08 Proper Name": proper, "09 Right Ascension": asc, "10 Declination": dec,
             "11 Distance (light years)": distance, "12 Proper Motion - R.A. (milliarcsec / year)": pmra,
             "13 Proper Motion - Dec. (milliarcsec / year)": pmdec, "14 Radial Velocity (km / sec)": rv,
             "15 Apparent Magnitude (V Magnitude)": mag, "16 Absolute Magnitude (V Magnitude)": abs_mag,
             "17 Spectral Type": spect,
             "18 Color Index (B-V)": ci, "19 x (light years)": x, "20 y (light years)": y, "21 z (light years)": z,
             "22 Velocity - x (parsecs / year)": vx, "23 Velocity - y (parsecs / year)": vy,
             "24 Velocity - z (parsecs / year)": vz, "25 Right Ascension (radians)": rarad,
             "26 Declination (radians)": decrad, "27 Proper Motion - Right Ascension": pmrarad,
             "28 Proper Motion - Declination": pmdecrad, "29 Bayer Designation": bayer, "30 Flamsteed Number": flam,
             "31 Constellation": con, "32 Luminosity (Solar Luminosities)": luminosity, "33 Variable Designation": var,
             "34 Var. Minimum (V Magnitude)": var_min, "35 Var. Maximum (V Magnitude)": var_max,
             "36 Main Sequence Lifespan": tau_ms, "37 Habitable Zone Inner (AU)": hz_inner,
             "38 Habitable Zone Outer (AU)": hz_outer, "39 Political": political, "40 Year Explored": year_explored,
             "41 Local ID": local_id, "42 System ID": system_id,
             "43 System Name": system_name, "44 Planets": planets, "45 Wormholes To": wormholes_to})
        print("Writing Stars XL")
        output.to_excel(path)

    def write_planets_xl(self, path: "str" = "SF_Cat_Planets"):

        i = len(path)
        if path[i - 5:] != ".xlsx":
            path += ".xlsx"

        self.planet_list.sort(key=lambda planet: planet.idn)

        ids = []
        name = []
        pl_type = []
        mass = []
        radius = []
        g = []
        period = []
        rot_period = []
        sma = []
        political = []
        star_name = []
        star_id = []
        local_id = []
        moons = []

        for planet in self.planet_list:
            print("Writing " + str(planet.idn) + ": " + planet.name)
            ids.append(planet.idn)
            name.append(planet.name)
            pl_type.append(planet.type)
            mass.append(planet.mass)
            radius.append(planet.radius)
            g.append(planet.g)
            period.append(planet.period)
            rot_period.append(planet.rot_period)
            sma.append(planet.sma)
            political.append(planet.political)
            star_name.append(planet.star_name)
            star_id.append(planet.star_id)
            local_id.append(planet.local_id)

            # The 'if' statement ensures that we don't wipe out the moons if they haven't been read in.
            if len(planet.moons) > 0:
                planet.moon_str = ""
                for moon in planet.moons:
                    planet.moon_str += str(moon.idn) + "; "
            moons.append(planet.moon_str)

        output = pd.DataFrame({"00 ID": ids, "01 Name": name, "02 Type": pl_type, "03 Mass (Earth masses)": mass,
                               "04 Radius (Earth radii)": radius, "05 Surface Gravity (ms^-2)": g,
                               "06 Orbital Period (yrs)": period, "07 Rotational Period (days)": rot_period,
                               "08 Semi-Major Axis (AU)": sma, "09 Political": political, "10 Star Name": star_name,
                               "11 Star ID": star_id, "12 Local ID": local_id, "13 direct": moons})
        print("Writing Planets XL")
        output.to_excel(path)

    def write_moons_xl(self, path: "str" = "SF_Cat_Moons"):

        print("On Start Write: " + str(len(self.moon_list)))

        i = len(path)
        if path[i - 5:] != ".xlsx":
            path += ".xlsx"
        self.moon_list.sort(key=lambda moon: moon.idn)

        ids = []
        name = []
        mass = []
        radius = []
        g = []
        sma = []
        period = []
        planet = []
        planet_id = []
        id_local = []
        political = []

        for moon in self.moon_list:
            print("Writing " + str(moon.idn) + ": " + moon.name)
            ids.append(moon.idn)
            name.append(moon.name)
            mass.append(moon.mass)
            radius.append(moon.radius)
            g.append(moon.g)
            sma.append(moon.sma)
            period.append(moon.period)
            planet.append(moon.planet_name)
            planet_id.append(moon.planet_id)
            id_local.append(moon.id_local)
            political.append(moon.political)

        output = pd.DataFrame(
            {"00 ID": ids, "01 Name": name, "02 Mass (kg)": mass, "03 Radius (m)": radius,
             "04 Surface Gravity (ms^-2)": g,
             "05 Semi-Major Axis (m)": sma, "06 Period (days)": period,
             "07 Planet": planet, "08 Planet ID": planet_id, "09 Local ID": id_local, "10 Political": political})
        print("Writing direct XL")

        output.to_excel(path)

        print("On Finish Write: " + str(len(self.moon_list)))

    def write_all_xl(self, moon_path: "str" = "SF_Cat_Moons", planet_path: "str" = "SF_Cat_Planets",
                     star_path: "str" = "SF_Cat_Stars", syst_path="SF_Cat_StarSystems"):

        self.write_moons_xl(moon_path)
        self.write_planets_xl(planet_path)
        self.write_stars_xl(star_path)
        self.write_systems_xl(syst_path)

    def write_systems(self, path: "str" = "SF_Cat_StarSystems"):
        """
        :param path: Name to which you wish to save the file.
        :return:
        """

        i = len(path)
        if path[i - 4:] != ".csv":
            path += ".csv"
        self.star_sys_list.sort(key=lambda syst: syst.idn)

        ids = []
        name = []
        stars = []

        for syst in self.star_sys_list:
            print("Writing " + str(syst.idn) + ": " + syst.name)
            ids.append(syst.idn)
            name.append(syst.name)

            # The 'if' statement ensures that we don't wipe out the stars if they haven't been read in.
            if len(syst.stars) > 0:
                syst.star_str = ""
                for star in syst.stars:
                    syst.star_str += str(star.idn) + "; "
            stars.append(syst.star_str)

        output = pd.DataFrame({"00 ID": ids, "01 Name": name, "02 Stars": stars})
        print("Writing StarSystem CSV")
        output.to_csv(path)

    def write_stars(self, path: "str" = "SF_Cat_Stars", sort=lambda star: star.idn):

        i = len(path)
        if path[i - 4:] != ".csv":
            path += ".csv"

        self.star_list.sort(key=sort)

        ids = []
        name = []
        mass = []

        hip = []
        hd = []
        hr = []
        gl = []
        bf = []
        proper = []
        asc = []
        dec = []
        distance = []
        pmra = []
        pmdec = []
        rv = []
        mag = []
        abs_mag = []
        spect = []
        ci = []
        x = []
        y = []
        z = []
        vx = []
        vy = []
        vz = []
        rarad = []
        decrad = []
        pmrarad = []
        pmdecrad = []
        bayer = []
        flam = []
        con = []
        luminosity = []
        var = []
        var_min = []
        var_max = []

        tau_ms = []
        hz_inner = []
        hz_outer = []
        political = []
        year_explored = []
        local_id = []
        system_id = []
        system_name = []
        planets = []
        wormholes_to = []

        for star in self.star_list:
            print("Writing " + str(star.idn) + ": " + star.name)
            ids.append(star.idn)
            mass.append(star.mass)
            name.append(star.name)

            hip.append(star.hip)
            hd.append(star.hd)
            hr.append(star.hr)
            gl.append(star.gl)
            bf.append(star.bf)
            proper.append(star.proper)
            asc.append(star.asc)
            dec.append(star.dec)
            distance.append(star.distance)
            pmra.append(star.pmra)
            pmdec.append(star.pmdec)
            rv.append(star.rv)
            mag.append(star.mag)
            abs_mag.append(star.abs_mag)
            spect.append(star.spec_type)
            ci.append(star.ci)
            x.append(star.x)
            y.append(star.y)
            z.append(star.z)
            vx.append(star.x)
            vy.append(star.y)
            vz.append(star.z)
            rarad.append(star.rarad)
            decrad.append(star.decrad)
            pmrarad.append(star.pmrarad)
            pmdecrad.append(star.pmdecrad)
            bayer.append(star.bayer)
            flam.append(star.flam)
            con.append(star.con)
            luminosity.append(star.luminosity)
            var.append(star.var)
            var_min.append(star.var_min)
            var_max.append(star.var_max)

            tau_ms.append(star.tau_ms)
            hz_inner.append(star.hz_inner)
            hz_outer.append(star.hz_outer)
            political.append(star.political)
            year_explored.append(star.year_explored)

            local_id.append(star.local_id)
            system_id.append(star.system_id)
            system_name.append(star.system_name)

            # The 'if' statement ensures that we don't wipe out the planets if they haven't been read in.
            if len(star.planets) > 0:
                star.planet_str = ""
                for planet in star.planets:
                    star.planet_str += str(planet.idn) + "; "
            planets.append(star.planet_str)
            wormholes_to.append(star.wormholes_to)

        output = pd.DataFrame(
            {"00 ID": ids, "01 Name": name, "02 Mass": mass, "03 HIP ID": hip, "04 HD ID": hd, "05 HR ID": hr,
             "06 GL ID": gl, "07 BF ID": bf, "08 Proper Name": proper, "09 Right Ascension": asc, "10 Declination": dec,
             "11 Distance (light years)": distance, "12 Proper Motion - R.A. (milliarcsec / year)": pmra,
             "13 Proper Motion - Dec. (milliarcsec / year)": pmdec, "14 Radial Velocity (km / sec)": rv,
             "15 Apparent Magnitude (V Magnitude)": mag, "16 Absolute Magnitude (V Magnitude)": abs_mag,
             "17 Spectral Type": spect,
             "18 Color Index (B-V)": ci, "19 x (light years)": x, "20 y (light years)": y, "21 z (light years)": z,
             "22 Velocity - x (parsecs / year)": vx, "23 Velocity - y (parsecs / year)": vy,
             "24 Velocity - z (parsecs / year)": vz, "25 Right Ascension (radians)": rarad,
             "26 Declination (radians)": decrad, "27 Proper Motion - Right Ascension": pmrarad,
             "28 Proper Motion - Declination": pmdecrad, "29 Bayer Designation": bayer, "30 Flamsteed Number": flam,
             "31 Constellation": con, "32 Luminosity (Solar Luminosities)": luminosity, "33 Variable Designation": var,
             "34 Var. Minimum (V Magnitude)": var_min, "35 Var. Maximum (V Magnitude)": var_max,
             "36 Main Sequence Lifespan": tau_ms, "37 Habitable Zone Inner (AU)": hz_inner,
             "38 Habitable Zone Outer (AU)": hz_outer, "39 Political": political, "40 Year Explored": year_explored,
             "41 Local ID": local_id, "42 System ID": system_id,
             "43 System Name": system_name, "44 Planets": planets, "45 Wormholes To": wormholes_to})
        print("Writing Stars CSV")
        output.to_csv(path)

    def write_planets(self, path: "str" = "SF_Cat_Planets"):

        i = len(path)
        if path[i - 4:] != ".csv":
            path += ".csv"

        self.planet_list.sort(key=lambda planet: planet.idn)

        ids = []
        name = []
        pl_type = []
        mass = []
        radius = []
        g = []
        period = []
        rot_period = []
        sma = []
        political = []
        star_name = []
        star_id = []
        local_id = []
        moons = []

        for planet in self.planet_list:
            print("Writing " + str(planet.idn) + ": " + planet.name)
            ids.append(planet.idn)
            name.append(planet.name)
            pl_type.append(planet.type)
            mass.append(planet.mass)
            radius.append(planet.radius)
            g.append(planet.g)
            period.append(planet.period)
            rot_period.append(planet.rot_period)
            sma.append(planet.sma)
            political.append(planet.political)
            star_name.append(planet.star_name)
            star_id.append(planet.star_id)
            local_id.append(planet.local_id)

            # The 'if' statement ensures that we don't wipe out the moons if they haven't been read in.
            if len(planet.moons) > 0:
                planet.moon_str = ""
                for moon in planet.moons:
                    planet.moon_str += str(moon.idn) + "; "
            moons.append(planet.moon_str)

        output = pd.DataFrame({"00 ID": ids, "01 Name": name, "02 Type": pl_type, "03 Mass (Earth masses)": mass,
                               "04 Radius (Earth radii)": radius, "05 Surface Gravity (ms^-2)": g,
                               "06 Orbital Period (yrs)": period, "07 Rotational Period (days)": rot_period,
                               "08 Semi-Major Axis (AU)": sma, "09 Political": political, "10 Star Name": star_name,
                               "11 Star ID": star_id, "12 Local ID": local_id, "13 direct": moons})
        print("Writing Planets CSV")
        output.to_csv(path)

    def write_moons(self, path: "str" = "SF_Cat_Moons"):

        i = len(path)
        if path[i - 4:] != ".csv":
            path += ".csv"
        self.moon_list.sort(key=lambda mn: mn.idn)

        ids = []
        name = []
        mass = []
        radius = []
        g = []
        sma = []
        period = []
        planet = []
        planet_id = []
        id_local = []
        political = []

        for moon in self.moon_list:
            print("Writing " + str(moon.idn) + ": " + moon.name)
            ids.append(moon.idn)
            name.append(moon.name)
            mass.append(moon.mass)
            radius.append(moon.radius)
            g.append(moon.g)
            sma.append(moon.sma)
            period.append(moon.period)
            planet.append(moon.planet_name)
            planet_id.append(moon.planet_id)
            id_local.append(moon.id_local)
            political.append(moon.political)

        output = pd.DataFrame(
            {"00 ID": ids, "01 Name": name, "02 Mass (kg)": mass, "03 Radius (m)": radius,
             "04 Surface Gravity (ms^-2)": g,
             "05 Semi-Major Axis (m)": sma, "06 Period (days)": period,
             "07 Planet": planet, "08 Planet ID": planet_id, "09 Local ID": id_local, "10 Political": political})
        print("Writing direct CSV")
        output.to_csv(path)

    def write_all(self, moon_path: "str" = "SF_Cat_Moons", planet_path: "str" = "SF_Cat_Planets",
                  star_path: "str" = "SF_Cat_Stars", syst_path="SF_Cat_StarSystems"):

        self.write_moons(moon_path)
        self.write_planets(planet_path)
        self.write_stars(star_path)
        self.write_systems(syst_path)


class StarSystem:
    """
        Attributes:
            x, y, z: cartesian coordinates of the star system in space
    """

    def __init__(self, name=None):

        self.name = str(name)
        self.idn = None
        self.star_str = ""
        self.stars = list()

        # TODO: Calculate barycentre

    def __getitem__(self, item):
        return self.stars[item]

    def add_star(self, star):
        if type(star) is Star:
            star.system = self
            self.stars.append(star)
            star.system_id = self.idn
            star.system_name = self.name
        else:
            raise TypeError('Argument must be of type astronomy.Star')

    def show(self):

        print('Star System')
        if self.name is not None:
            print('Name: ' + str(self.name))
        if self.stars != list():
            self.stars.sort(key=lambda s: s.mass)
            print('Stars: ')
            print('')

            for star in self.stars:
                star.show()
                print('')

        return

    def show_min(self):

        if self.name is not None:
            print('Star System: ' + str(self.name))
        else:
            print('Star')

        if self.stars != list():
            self.stars.sort(key=lambda s: s.mass)
            for s in self.stars:
                s.show_min()

    def populate(self, num=None):

        # TODO: Finish this
        if num is None:
            num = r.randint(0, 100)


class Star:
    """
    Variables such as luminosity and habitable zone are approximations valid only on the main sequence.
    Attributes:
        mass: mass of the star in Solar Masses
        luminosity: luminosity of the star in Solar units
        tau_ms: main-sequence lifespan of the star
        hz_inner: Inner border of the star's habitable zone, in AU
        hz_outer: outer border of the star's habitable zone, in AU
        temp_eff: effective temperature of the star
    """

    def __init__(self, name=None, mass=None, create=False):

        # Names and IDs
        if name is not None:
            self.name = str(name)
        else:
            self.name = None
        self.names: "list" = []
        self.idn: "int" = None
        self.hip: "int" = None  # HIP catalogue id
        self.hd: "int" = None  # HD catalogue id
        self.hr: "str" = None  # HR catalogue id
        self.gl: "str" = None  # GL catalogue id - also includes GJ
        self.wise: "str" = None  # WISE catalogue id
        self.wisep: "str" = None  # WISEP catalogue id
        self.wisepc: "str" = None  # WISEPC Catalogue id
        self.two_mass: "str" = None  # 2MASS catalogue id
        self.sdss: "str" = None  # SDSS catalogue id
        self.epic: "str" = None  # EPIC catalogue id
        self.sao: "str" = None  # SAO catalogue id
        self.bf: "str" = None
        self.proper: "str" = None
        self.bayer = None
        self.flam = None
        self.con = None

        # Position
        self.asc: "float" = None
        self.dec: "float" = None
        self.distance: "float" = None
        self.x: "float" = None
        self.y: "float" = None
        self.z: "float" = None

        self.asc_hours = None
        self.asc_mins = None
        self.asc_sec = None
        self.dec_hours = None
        self.dec_mins = None
        self.dec_sec = None

        # Motion
        self.pmra: "float" = None
        self.pmdec: "float" = None
        self.rv: "float" = None
        self.vx: "float" = None
        self.vy: "float" = None
        self.vz: "float" = None
        self.rarad: "float" = None
        self.decrad: "float" = None
        self.pmrarad: "float" = None
        self.pmdecrad = None

        # Properties
        if type(mass) is float:
            self.mass = float(mass)
        else:
            self.mass = None
        self.radius: "float" = None
        self.mag: "float" = None
        self.abs_mag: "float" = None
        self.spec_type: "str" = None
        self.ci: "float" = None
        self.luminosity = None
        self.var = None
        self.var_min = None
        self.var_max = None
        self.temp_eff = None
        self.tau_ms = None  # yrs
        self.age: "float" = None  # yrs
        self.metallicity: "float" = None

        # System
        self.system: "StarSystem" = None
        self.local_id = None
        self.system_id = None
        self.system_name = None
        self.planet_str = ""
        self.planets = list()
        self.wormholes_to = ""
        self.hz_inner = None
        self.hz_outer = None
        self.sma = None

        self.nearest_neighbour = None
        self.nearest_neighbour_d = None

        # Exploration
        self.political: "str" = None
        self.year_explored: "int" = None
        self.visited = False

        if create is True:
            if mass is None:
                self.recalculate(mass=True)
            else:
                self.recalculate()

    def distance_to(self, star):
        """
        Calculates the distance to a given star, in light years
        :param star: The other Star object. Must have coordinates set.
        :return: Distance in ly.
        """

        d = distance_between(self.x, self.y, self.z, star.x, star.y, star.z)

        return d

    def recalculate(self, mass=False):
        if mass is True:
            self.det_mass()

        self.ms_luminosity()
        self.ms_habzone()
        self.ms_lifespan()
        # self.temperature()

    def det_mass(self):
        self.mass = ma.prob_from_distribution(masses_def, pdmf_def)
        return self.mass

    def ms_habzone(self):
        """Given the star's luminosity, this calculates its habitable zone
        Habitable zone: http://www.planetarybiology.com/calculating_habitable_zone.html
        """
        # If the values we need are not there, calculate them.
        if self.luminosity is None:
            if self.mass is None:
                self.det_mass()
                self.ms_luminosity()
            else:
                self.ms_luminosity()

        l = float(self.luminosity)
        inner = math.sqrt(l / 1.1)
        outer = math.sqrt(l / 0.53)
        self.hz_inner = inner
        self.hz_outer = outer
        return inner, outer

    def ms_lifespan(self):
        """
        Calculates the main sequence lifespan of the star
        From: https://en.wikipedia.org/wiki/Main_sequence#Lifetime
        :return: Main-sequence lifespan in years
        """
        if self.mass is None:
            self.det_mass()
        if self.luminosity is None:
            self.ms_luminosity()

        m = float(self.mass)

        life = (10. ** 10.) * (m ** (-2.5))
        self.tau_ms = life
        return self.tau_ms

    def ms_luminosity(self):
        """
        Given the star's mass, this calculates its luminosity ON THE MAIN SEQUENCE
        Mass-luminosity relationship: https://en.wikipedia.org/wiki/Mass%E2%80%93luminosity_relation
        :return:
        """

        if self.mass is None:
            self.det_mass()

        s = float()
        a = float()
        m = float(self.mass)
        if m < 0.43:
            s = 0.23
            a = 2.3
        elif m < 2:
            s = 1.
            a = 4.
        elif m < 20:
            s = 1.5
            a = 3.5
        else:
            s = 3200.
            a = 1.

        self.luminosity = s * (m ** a)
        return self.luminosity

    def add_planet(self, planet):
        if type(planet) is Planet:
            planet.star = self
            planet.star_id = self.idn
            planet.star_name = self.name
            self.planets.append(planet)
        else:
            raise TypeError('Argument must be of type astronomy.Planet')

    def set_nearest_neighbour(self, s):
        if type(s) is Star:
            self.nearest_neighbour = s
        else:
            raise TypeError('Argument must be of type astronomy.StarSystem')

    def show(self):
        if self.name is not None:
            print('Name: ' + str(self.name))
        if self.mass is not None:
            print('Mass: ' + str(self.mass) + ' M_sol')
        if self.tau_ms is not None:
            print('Lifespan: ' + str(self.tau_ms) + ' years')
        if self.hz_inner is not None and self.hz_outer is not None:
            print('Habitable Zone: ' + str(self.ms_habzone()) + ' AU')
        if self.planets != list():
            self.planets.sort(key=lambda pl: pl.sma)
            print('')
            print('Planets: ')
            for p in self.planets:
                p.show()
                print('')

    def show_min(self):

        if self.name is not None:
            print('    Star: ' + str(self.name))
        else:
            print('    Star')

        if self.planets != list():
            self.planets.sort(key=lambda pl: pl.sma)
            for p in self.planets:
                p.show_min()

    def match_star(self, list: "StarList", tolerance=0.05):
        for star in list:
            delta_asc = abs(star.asc-self.asc)
            if delta_asc < tolerance:
                delta_dec = abs(star.dec-self.dec)
                if delta_dec < tolerance:
                    # TODO: INCOMPLETE
                    a = 3



class Planet:
    """
    Attributes:
        mass: mass of the planet, in Earth masses
        radius: radius of the planet, in metres
        sma: semi-major axis of the planet's orbit, in AU
    """

    def __init__(self, mass=None, radius=None, name=None):

        # Exploration
        self.name = name
        self.names = []
        self.political: "str" = ""  # Political information
        self.discovered: "int" = None  # Year discovered
        self.detection: "str" = None  # Detection method of discovery
        self.mass_det_type: "str" = None  # Mass detection method
        self.rad_det_type: "str" = None  # Radius detection method

        # Intrinsic properties
        self.type = ""
        self.mass = mass  # Earth masses
        self.radius = radius
        self.g = None
        self.temp: "float" = None  # Temperature, in K
        self.geometric_albedo: "float" = None  # Geometric albedo
        self.molecules: "str" = None  # Molecules observed

        # Orbital characteristics
        self.period: "float" = None  # Orbital period, in days
        self.rot_period: "float" = None
        self.sma: "float" = None  # Semi-major axis, in AU
        self.eccentricity: "float" = None
        self.inclination: "float" = None # Orbital inclination, in degrees
        self.omega: "float" = None  # Argument of periastron, in degrees
        self.semi_amplitude: "float" = None  # Semi-amplitude (I don't know what this means either)

        # System
        self.star_name = ""
        self.star_id = None
        self.local_id = None
        self.star = Star()

        self.moons_str = ""
        self.moons = list()

    def det_mass(self):
        # Planet mass distribution and mass-radius relationship: https://arxiv.org/pdf/1502.05011v2.pdf

        logm = r.normal(0.8, 1.15)  # Earth masses, assuming peak of 0.8 log(m/M_E)
        self.mass = 10. ** (logm)

    def surface_g(self):
        return u.G * self.mass / self.radius ** 2

    def set_star(self, star):
        self.star = star

    def det_orbit(self):
        try:
            pi = math.pi
            a = u.length_to_metre(self.sma, units='AU')
            G = u.G
            M = u.mass_to_kg(self.star.mass, units='M_sol')

            T = 2 * pi * math.sqrt((a ** 3.) / (G * M))  # in seconds
            self.period = u.time_from_sec(T, units='yr')  # convert to years
        except TypeError:
            print("Some of your values are None. Make sure star and sma are assigned correctly.")

    def add_moon(self, moon):
        if type(moon) is Moon:
            moon.planet = self
            self.moons.append(moon)
        else:
            raise TypeError('Argument must be of type astronomy.Moon')

    # def populate_moons(self, n):
    #     for i in range(n):


    def show(self):

        if self.name is not None:
            print('   Name: ' + self.name)
        if self.mass is not None:
            print('   Mass: ' + str(self.mass) + ' M_Earth')
        if self.radius is not None:
            print('   Radius: ' + str(self.radius))
        if self.sma is not None:
            print('   Semi-Major Axis: ' + str(self.sma))
        if self.period is not None:
            print('   Period: ' + str(self.period))

        if self.moons != list():
            self.moons.sort(key=lambda m: m.sma)
            print('')
            print('direct: ')
            for m in self.moons:
                m.show()
                print('')

    def show_min(self):

        if self.name is not None:
            print('        Planet: ' + str(self.name))
        else:
            print('        Unnamed Planet')

        if self.moons != list():
            self.moons.sort(key=lambda m: m.sma)
            for m in self.moons:
                m.show_min()

    def write_to_file(self, title):

        outputvalues = np.zeros([len(self.moons), 7], dtype=(str, 24))

        for i, moon in enumerate(self.moons):
            outputvalues[i, 0] = str(i)
            outputvalues[i, 1] = str(moon.name)
            outputvalues[i, 2] = str(moon.mass)
            outputvalues[i, 3] = str(moon.radius)
            outputvalues[i, 4] = str(moon.sma)
            outputvalues[i, 5] = str(moon.period)

        np.savetxt(title + '.txt', outputvalues, fmt='%-11s %-11s %-11s %-11s %-11s %-11s')


class Moon:
    def __init__(self, mass=None, radius=None, name=None, idn=None):
        self.idn = idn
        self.name = name
        self.mass = mass  # In Earth masses
        self.radius = radius
        self.g = None
        self.sma = None
        self.period = None
        self.planet = Planet()
        self.planet_name: "str" = ""
        self.planet_id: "int" = None
        self.id_local = None
        self.political = ""

    def set_planet(self, planet):
        self.planet = planet

    def det_orbit(self):
        try:
            pi = math.pi
            a = u.length_to_metre(self.sma, units='AU')
            G = u.G
            M = u.mass_to_kg(self.planet.mass, units='M_E')

            T = 2 * pi * math.sqrt((a ** 3.) / (G * M))  # in seconds
            self.period = u.time_from_sec(T, units='yr')  # convert to years

        except TypeError:
            print("Some of your values are None. Make sure star and sma are assigned correctly.")

    def show(self):

        if self.name is not None:
            print('      Name: ' + self.name)
        if self.mass is not None:
            print('      Mass: ' + str(self.mass) + ' M_Earth')
        if self.radius is not None:
            print('      Radius: ' + str(self.radius))
        if self.sma is not None:
            print('      Semi-Major Axis: ' + str(self.sma))
        if self.period is not None:
            print('      Period: ' + str(self.period))

    def show_min(self):

        if self.name is not None:
            print('            Moon: ' + str(self.name))
        else:
            print('            Unnamed Moon')


def imf(mass):
    """
    Returns the frequency of a given mass under the initial mass function
    # Star initial mass function and present-day mass function: https://arxiv.org/pdf/astro-ph/0304382.pdf
    :param mass: mass of star
    :return: frequency
    """
    if mass <= 1:
        return 0.158 * math.exp(-((math.log10(mass) - math.log10(0.079)) ** 2) / (2 * 0.69 ** 2))
    else:
        return 4.43 * 10 ** (-2) * mass ** (-1.3)


def pdmf(mass):
    """
    Returns the frequency of a given mass under the present-day mass function
    # Star initial mass function and present-day mass function: https://arxiv.org/pdf/astro-ph/0304382.pdf
    :param mass: mass of star
    :return:
    """
    A = float()
    x = float()
    if mass <= 1:
        return 0.158 * math.exp(-((math.log10(mass) - math.log10(0.079)) ** 2) / (2 * 0.69 ** 2))
    else:
        if math.log10(mass) <= 0.54:
            A = 4.4 * 10 ** (-2.)
            x = 4.37
        elif math.log10(mass) <= 1.26:
            A = 1.5 * 10 ** (-2.)
            x = 3.53
        else:
            A = 2.5 * 10 ** (-4.)
            x = 2.11

        return A * mass ** -x


def imf_pdmf(mn, mx):
    mass = np.arange(mn, mx, step=0.001, dtype=float)
    imf_arr = np.zeros(mass.size)
    pdmf_arr = np.zeros(mass.size)

    for i, m in enumerate(mass):
        imf_arr[i] = imf(m)
        pdmf_arr[i] = pdmf(m)

    maxim = max(imf_arr)

    imf_arr = imf_arr / maxim
    pdmf_arr = pdmf_arr / maxim

    return imf_arr, pdmf_arr


dists = imf_pdmf(0.001, 315)

imf_def = dists[0]
pdmf_def = dists[1]

masses_def = np.arange(0.001, 315, step=0.001, dtype=float)


def distance_between(x1, y1, z1, x2, y2, z2):
    '''
    :param x1:
    :param y1:
    :param z1:
    :param x2:
    :param y2:
    :param z2:
    :return: Distance between points (x1,y1,z1) and (x2,y2,z2).
    '''
    return math.sqrt((x2 - x1) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


def equ_to_cart(asc_hrs, asc_mins, asc_sec, dec_deg, dec_mins, dec_sec, distance):
    """

    Convert celestial coordinates of stars in the sky to Cartesian coordinates with Earth/Sun at the origin.

    This cartesian system uses:
        + x axis: towards dec=0, asc=0 (vernal equinox)
        + y axis: towards dec=0, asc=6 hrs
        + z axis: towards dec = 90 (north celestial pole)

    :param asc_hrs: The hour component of the right ascension, in hours
    :param asc_mins: The minute component of the right ascension, in minutes
    :param asc_sec: The second component of the right ascension, in seconds
    :param dec: Declination, in degrees
    :param distance: Distance, in light years (or other units)
    :return: numpy array of three Cartesian coordinates, x,y,z
    """

    # First convert right ascension to degrees

    # For R.A., the entire thing is multiplied by 15
    asc = u.angle_ra_to_radians(asc_hrs, asc_mins, asc_sec)
    # asc = 15. * (float(asc_hrs) + (1. / 60.) * float(asc_mins) + (1. / 3600.) * float(asc_sec))
    dec = u.angle_arc_to_decimal(dec_deg, dec_mins, dec_sec, radians=True)

    # Now convert to Cartesian coordinates
    x = float(distance) * math.cos(dec) * math.cos(asc)
    y = float(distance) * math.cos(dec) * math.sin(asc)
    z = float(distance) * math.sin(dec)

    return x, y, z


SolSystem = StarSystem(name='Sol System')
SolSystem.x = 0.
SolSystem.y = 0.
SolSystem.z = 0.

Sun = Star(name='The Sun')
Sun.mass = 1.
Sun.luminosity = 1.
