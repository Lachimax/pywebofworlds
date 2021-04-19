from src.pywebofworlds import physics as u
import math

c = u.c


def gamma(v):
    """
    Calculates the gamma (Lorentz) factor for an object travelling at speed v.
    :param v: Speed of object, in m/s
    :return: Gamma factor
        gamm = 1. / math.sqrt(1. - (v / c) ** 2.)
    """
    if (v >= 0) & (v < c):
        v = float(v)
        return (math.sqrt(1-(v/c)**2))**-1

    else:
        raise ValueError('v must be less than the speed of light')


def kinetic_energy(m, v):
    """
    Calculates relativistic kinetic energy of an object.
    :param m: Mass of the object, in kg
    :param v: Speed of the object, in m/s
    :return:
    """
    v = float(v)
    g = gamma(v)

    ke = g * mass_energy(m) - mass_energy(m)
    return ke


def mass_energy(m):
    """
    Calculates the mass-energy of an object
    :param m: mass of object, in kg
    :return: mass-energy, in joules
    """
    m = float(m)
    e = m * c ** 2
    return e


def energy_mass(E):
    """
    Calculates the mass of a given mass
    :param E:
    :return:
    """

    m = E / c ** 2
    return m


def time_dilation(t, v):
    """
    Calculates the PROPER TIME elapsed in the reference frame of the moving object, given the coordinate time
    :param t:
    :param v:
    :return:
    """

    v = float(v)
    t_prime = float(t)
    t = t_prime / gamma(v)

    return t
