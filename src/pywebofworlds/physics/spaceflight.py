from src.pywebofworlds import physics as u, physics as a, physics as m
import src.pywebofworlds.physics.relativity as r
import math
import matplotlib.pyplot as plt
import numpy as np
from queue import *

c = u.c


# TODO: For wormhole networks, implement increasing speeds
# TODO: Select stars along line? - directed creep, select closest star to point in sky


def distance_travelled(t, g=10., v0=0.):
    """
    Calculates the distance travelled under constant acceleration for a given time
    :param t: Time elapsed in s (coordinate time)
    :param g: acceleration in ms^-2
    :param v0: initial velocity in m/s
    :return: Distance travelled, in m
    """

    g = float(g)
    v0 = float(v0)

    gamma_0 = r.gamma(v0)

    x = (c ** 2. / g) * (math.sqrt(1. + (g * t + v0 * gamma_0) ** 2. / c ** 2.) - gamma_0)

    return x


def velocity(t, v0=0., g=10.):
    """
    Calculates the velocity after constant acceleration for a given time
    :param v0: initial velocity
    :param t: coordinate time passed, in s
    :param g: acceleration, in ms^-2
    :return:
    """

    v0 = float(v0)
    g = float(g)

    gamma0 = r.gamma(v0)

    v = (v0 * gamma0 + g * t) / math.sqrt(1 + ((v0 * gamma0 + g * t) / c) ** 2)
    return v


def coord_time(x, g=10.):
    """
    Calculates the coordinate time to have passed when a constantly-accelerating object has travelled a distance x.
    :param g: Acceleration of the spacecraft in ms^-2
    :param x: Distance travelled by the spacecraft in m
    :return: Coordinate time passed, in s
    """

    x = float(x)
    g = float(g)

    t = (c / g) * math.sqrt(((g * x / c ** 2) + 1) ** 2 - 1)

    return t


def proper_time(t, g=10.):
    """
    Calculates the proper time to have passed in the reference frame of a spacecraft under constant acceleration
    :param t: coordinate time, in s
    :param g: acceleration of the spacecraft in ms^-2
    :return: proper time elapsed, in s
    """

    t = float(t)

    tau = (c / g) * math.log((g * t / c) + math.sqrt(1 + (g * t / c) ** 2))

    return tau


class Voyage:
    """
    A class intended to represent a single star-to-star journey by a spacecraft that accelerates constantly first,
    coasts for some time after, and then decelerates at the same rate as the initial acceleration the rest of the way.
    """

    def __init__(self, star1: 'a.Star', star2: 'a.Star', mass: 'float', g: 'float' = 10, g_time: 'float' = 0.5):
        """

        :param star1: A physics.astrophysics.star object, the spacecraft's origin.
        :param star2: A physics.astrophysics.star object, the spacecraft's destination.
        :param mass:
        :param g:
        :param g_time:
        """
        if type(star1) is a.Star:
            self.origin = star1
        else:
            raise ValueError('sys1 and sys2 must be of type Star')
        if type(star2) is a.Star:
            self.destination = star2
        else:
            raise ValueError('sys1 and sys2 must be of type Star')
        self.distance = u.length_to_metre(self.origin.distance_to(self.destination), units='ly')
        self.g = float(g)

        self.t_acc = u.time_to_sec(float(g_time), units='yr')

        self.v_coast = velocity(self.t_acc, g=self.g)

        self.x_acc = distance_travelled(self.t_acc, self.g)

        self.t_coast = (self.distance - 2 * self.x_acc) / self.v_coast
        self.t = self.coord_time()

        self.tau_acc = proper_time(self.t_acc, self.g)
        self.tau_coast = r.time_dilation(self.t_coast, self.v_coast)
        self.tau = self.proper_time()

        self.K = r.kinetic_energy(mass, self.v_coast)
        self.fuel_mass = 2 * r.energy_mass(self.K)

    def coord_time(self):
        t = self.t_acc * 2 + self.t_coast
        return t

    def proper_time(self):

        tau = 2 * self.tau_acc + self.tau_coast

        return tau


class Odyssey:
    """
    Intended to represent a chain of Voyages, from star to star.
    """

    def __init__(self, voyage_list: "list" = None):
        self.voyage_list = []
        if voyage_list is not None:
            self.voyage_list = voyage_list

    def add_voyage(self, voy: "Voyage"):
        if type(voy) is Voyage:
            self.voyage_list.append(voy)

    def coord_time(self):

        s = 0

        for voy in self.voyage_list:
            s += voy.t

    def proper_time(self):

        s = 0

        for voy in self.voyage_list:
            s += voy.tau

        return s


class WormholeGraph:
    def __init__(self, star_list, empire="Human"):
        self.vertex_list = list()
        self.size = 0
        self.empire = empire
        self.starList = a.StarList()
        self.set_star_list(star_list)
        self.star_num = len(self.starList.star_list)

    def __getitem__(self, item):
        return self.vertex_list[item]

    def set_star_list(self, star_list):
        if type(star_list) is a.StarList:
            self.starList = star_list
        else:
            raise ValueError("Argument must be of type astronomy.StarList")

    def furthest_outpost(self):
        """
        Returns the vertex with the greatest distance from the origin.
        :return:
        """

        maxim = 0.
        furthest = None
        for vert in self:
            star = vert.star
            if star.distance > maxim:
                maxim = star.distance
                furthest = vert

        return furthest

    def last_outpost(self):
        """
        Returns the vertex that was created last.
        :return:
        """

        maxim = 0.
        latest = None
        for vert in self:
            if vert.time > maxim:
                maxim = vert.time
                latest = vert

        return latest

    def single_creep(self, start=0, iterations=50, speed=0.5):
        """
        Builds a wormhole network by travelling from one star to its closest unvisited neighbour, one at a time.
        :param start: The index, in starList, of the desire
        :param iterations:
        :param speed: the speed the wormhole probes can move, as a fraction of the speed of light
        :return:
        """

        iterations = int(iterations)
        speed = float(speed)

        current = WormholeVertex(self.starList[start], 0)
        self.add_vertex(current)
        s = current.star
        time = 0
        i = 0
        while self.size < self.star_num and i < iterations:
            s.visited = True
            # iterate
            i += 1
            # Work out how long it takes for the next probe to get there, and add that to the current time
            catch = self.starList.find_unvisited_neighbour(s)
            dt = catch[1] / speed
            time += dt

            nex = WormholeVertex(catch[0], time)
            self.add_vertex(nex)
            current.add_wormhole(nex)

            current = nex
            # Set time in current to the time when we got there
            current.time = time
            s = current.star

        self.starList.reset_visits()

    def multi_creep(self, current=None, i=0, time=0., iterations=50, speed=0.5, max_wormholes=5):
        """
        Builds a wormhole network by
        :param current:
        :param i:
        :param time:
        :param iterations:
        :param speed:
        :param max_wormholes:
        :return:
        """

        if type(current) is WormholeVertex or current is None:

            if current is None:
                current = WormholeVertex(self.starList[0], time)
                self.add_vertex(current)

            i = int(i)
            iterations = int(iterations)
            speed = float(speed)
            s = current.star
            s.visited = True
            print(
                str(self.size) + ". i = " + str(i) + "; HIP: " + str(s.idn) + "; Name: " + s.name + "; Time:" + str(
                    time))

            if i < iterations:

                for j in range(max_wormholes):
                    catch = self.starList.find_unvisited_neighbour(s)
                    object_next = catch[0]
                    dist = catch[1]
                    if object_next is None:
                        break
                    dt = dist / speed
                    nxt = WormholeVertex(object_next)
                    self.add_vertex(nxt)
                    current.add_wormhole(nxt)

                    self.multi_creep(nxt, i + 1, time + dt, iterations, speed, max_wormholes)

        else:
            raise ValueError("object must be of type astronomy.StarSystem")

        self.starList.reset_visits()

    def bf_creep(self, num=100, degree=5,
                 speed=lambda t: 0.1 * math.exp(0.0016 * t) / math.sqrt(
                     1 + (0.1 * math.exp(0.0016 * t)) ** 2),
                 wait=lambda t: abs(np.random.normal(loc=100 * math.exp(-0.005 * t), scale=50)),
                 plot=False, start_date=0., end_date=None):
        """
        Attempts to model the spread of an interstellar wormhole-capable civilization, using Verse 12 rules and a
        breadth-first algorithm for finding nearby stars.
        When generating its wormholes, each vertex must create a connection to at least one unvisited system; but it
        may also create connections to visited systems.
        :param num:
        :param degree:
        :param speed: A function that decides how fast a wormhole probe can travel, as a function of time - to represent
        technological development. This decides how long it takes for a new wormhole to appear in a nearby system. This
        should, in effect, give the average speed of the probe over its journey.
        :param wait: A function that decides how long it should be between probe launches from a star, as a function of
        time (again, technological development).
        :param plot: If True, plots the resulting wormhole network using pyplot. Warning: large networks can take a lot
        longer to plot than to model in the first place.
        :param start_date: the year in which the first wormhole probe is launched; ie, the start of the civilization's
        spread. Defaults to 0.
        :param end_date: The cut-off date for the end of the model.
        :return:
        """

        q = Queue(num + degree)

        sl = self.starList

        s = self.starList[0]
        whv = WormholeVertex(s, 0, self.empire)
        self.add_vertex(whv)

        while self.size < num:

            print("Wormholes from: " + str(s.idn) + ": " + str(s.name))

            # Generate the waiting time for probes; sort by size because naturally the closest stars would be visited
            # first. Waiting time should be zero for first probes sent.
            waits = []
            for i in range(degree):
                if self.starList[0] is not whv.star:
                    waits.append(wait(whv.time))
                else:
                    waits.append(0)
            waits.sort()

            i = 0
            while i < degree - 1 and not q.full():
                if q.empty():
                    print("Queue is empty")

                # Look for a neighbour of the system that has not been visited
                ssn = sl.find_unvisited_neighbour(s)[0]
                if ssn is None:
                    break

                # Time to get to new system
                dt = s.distance_to(ssn) / speed(whv.time + waits[i]) + waits[i]

                # Check if that new system already has a wormhole, and create one if it doesn't.
                whn, add = self.check_for_vertex(ssn, whv.time + dt)
                # add, at this point, is True if the star already had a wormhole; we want to reverse this.
                add = not add

                ssn.visited = True

                # Add that system's wormhole vertex to this system's list of connections.
                whv.add_wormhole(whn)
                # If this star already had a wormhole, don't add it to the queue, because it's either already in there
                # or already been popped.
                if add and not q.full():
                    q.put(whn)

                i += 1

            # Find one more star that does not have a wormhole.

            ssn = sl.find_unvisited_neighbour(s)[0]
            dt = s.distance_to(ssn) / speed(whv.time + waits[i]) + waits[len(waits) - 1]
            # ssn is None = There are no unvisited systems. Should not happen in bf_creep
            if ssn is None:
                break
            catch = self.check_for_vertex(ssn, whv.time + dt)
            is_vertex = catch[1]
            whn = catch[0]

            while is_vertex:
                ssn = sl.find_unvisited_neighbour(s)[0]
                ssn.visited = True
                catch = self.check_for_vertex(ssn, whv.time + dt)
                is_vertex = catch[1]
                whn = catch[0]

            whv.add_wormhole(whn)
            q.put(whn)

            if q.full():
                print("Queue is full")

            whv.reset_visits()

            # Animate
            if plot:
                mp = plt.figure()

                self.plot_wormholes(mp, all_stars=False, line=False, colour="red")
                filename = str(self.size) + "bf\\_wormholes_" + str(whv.star.name + ".png")
                mp.savefig(filename)

            # Pull from queue
            whv = None
            if not q.empty():
                whv = q.get()
            if end_date is not None:
                while whv.time > end_date - start_date and not q.empty():
                    whv = q.get()

            s = whv.star

            if q.empty():
                print("Queue is empty")
                break

        print("Resetting visits")
        for w in self:
            w.star.year_explored += start_date

        self.write_wormholes_to()

    def directed_leap(self, start, end, limit):

        self.starList.star_list.sort(key=lambda s: s.distance_to(start))

        point1 = (start.x, start.y, start.z)
        point2 = (end.x, end.y, end.z)

        on_axis = []

        for star in self.starList:

            # Check if star is in between the two stars in some way
            if min(start.x, end.x) <= star.x <= max(start.x, end.x) \
                    and min(start.y, end.y) <= star.y <= max(start.y, end.y) \
                    and min(start.z, end.z) <= star.z <= max(start.z, end.z):

                pos = (star.x, star.y, star.z)
                if m.perp_distance(pos, point1, point2) < limit:
                    on_axis.append(star)
                    star.visited = True
                    whv = WormholeVertex(star, 0, self.empire)
                    if self.vertex_list:
                        whv.add_wormhole(self.vertex_list[-1])
                    self.add_vertex(whv)

    def write_wormholes_to(self):
        print("Writing wormholes to StarList")
        for wh in self:
            wh_str = ""
            print("Writing wormholes from: " + str(wh.star.idn) + ": " + wh.star.name)
            for other in wh:
                print("   To " + str(other.star.idn) + ": " + other.star.name)
                wh_str += str(other.star.idn) + "; "
            wh.star.wormholes_to = wh_str
        print("Finished writing wormholes to StarList")

    def add_vertex(self, vertex):
        if type(vertex) is WormholeVertex:
            self.vertex_list.append(vertex)
            self.size += 1
            ssn = vertex.star
            print(
                "   " + str(self.size) + " To " + str(
                    ssn.idn) + ": Name: " + ssn.name + "; Time: " + str(vertex.time))
            return vertex

        else:
            raise ValueError("ss must be of type WormholeVertex")

    def check_for_vertex(self, star, time):
        """
        Checks if there is a wormhole at a star - if so, returns that wormhole and True, and if not adds a new wormhole
        and returns that wormhole, and False. Also updates the time that wormhole was reached to the shorter of the two.
        :param star:
        :param time:
        :return:
        """

        for wh in self.vertex_list:
            if wh.star is star:
                if time is not None and wh.time > time:
                    wh.time = time
                return wh, True

        return self.add_vertex(WormholeVertex(star, time, self.empire)), False

    def plot_wormholes(self, mp=plt.figure(), all_stars=False, line=False, colour="red", suppress=True):
        """
        Uses pyplot to produce a 3D plot of the wormhole network. Caution - large networks take a long time to plot.
        :param mp: The pyplot figure to be adapted.
        :param all_stars:
        :param line: If True, plots black lines representing wormhole connections between vertices.
        :param colour: The Colour of the wormhole vertices to be plotted.
        :param suppress: If True, prevents the plot from being shown; useful if you want to plot several things at once.
        :return:
        """
        ax = mp.add_subplot(111, projection='3d')

        if all_stars:

            for s in self.starList:
                print("Plotting " + str(s.idn) + ": " + s.name)

                ax.scatter(xs=s.x, ys=s.y, zs=s.z, c="black", s=2)

                if line:
                    ax.plot(xs=[s.x, s.x], ys=[s.y, s.y], zs=[s.z, 0], c='black')
                    ax.plot(xs=[s.x, 0], ys=[s.y, 0], zs=[0, 0], c='black')

        for v in self.vertex_list:

            s = v.star
            print("Plotting " + str(s.idn) + ": " + s.name)

            ax.scatter(xs=s.x, ys=s.y, zs=s.z, c=colour, s=4)

            if line:
                ax.plot(xs=[s.x, s.x], ys=[s.y, s.y], zs=[s.z, 0], c='black')
                ax.plot(xs=[s.x, 0], ys=[s.y, 0], zs=[0, 0], c='black')

        for v in self:

            s = v.star
            print("Plotting wormholes from " + str(s.idn) + ": " + s.name)

            for j in v.wormholes:
                ssw = j.star
                print("   To " + str(ssw.idn) + ": " + ssw.name)
                ax.plot(xs=[ssw.x, s.x], ys=[ssw.y, s.y], zs=[ssw.z, s.z], c=colour)

        if not suppress:
            plt.show(mp)
        return mp

    def show(self):
        for wh in self:
            print(wh.star.name)

    def find_nearest_wh(self, wormhole):
        if type(wormhole) is WormholeVertex:
            wormholes = a.StarList()
            for wh in self:
                wormholes.add_star(wh.star)
            nrst, dist = wormholes.find_nearest_neighbour(wormhole.star)
            return self.check_for_vertex(nrst, None)[0], dist
        else:
            raise ValueError("wormhole must be of type WormholeVertex")

    def find_wormhole(self, name: "str"):
        if type(name) is str:
            for wh in self.vertex_list:
                if wh.star.name == name:
                    return wh

            return None

        else:
            raise ValueError("name must be a string")


class WormholeVertex:
    def __init__(self, star, time=None, empire="Human"):
        self.star = star
        self.wormholes = list()
        self.time = time
        self.star.year_explored = time
        self.star.political = empire

    def __getitem__(self, item):
        return self.wormholes[item]

    def reset_visits(self):
        for wh in self:
            wh.star.visited = False

    def add_wormhole(self, vertex):
        if type(vertex) is WormholeVertex and vertex not in self.wormholes:
            self.wormholes.append(vertex)
            vertex.wormholes.append(self)


def plot_networks(networks, all_stars=False, bl=False):
    mp = plt.figure()

    colours = ["red", "green", "blue", "purple", "cyan", "orange"]

    for i, j in enumerate(networks):
        mp = j.plot_wormholes(mp, all_stars, bl, colours[i])

    plt.show(mp)
