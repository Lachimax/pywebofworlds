import math

# TODO: Allow entry of raw number into 'units' argument of each function, ie allow custom units as multiples of the base unit

pi = math.pi

# CONSTANTS

# Avogadro Constant (N_A)
N_A = 6.022140857e23  # mol^-1
# Boltzmann Constant (k_B)
k_B = 1.3806488e-23  # J K^-1
# Gravitational Constant (G)
G = 6.67408e-11  # m^3 kg^-1 s^-2
# Speed of light in a vacuum
c = 299792458.  # m/s

# Planck Constant (h)
h = 6.626070040e-34  # J s
# Reduced Planck Constant (h_bar)
h_bar = h / 2 * pi  # J s

# Vacuum Permeability (mu_0)
mu_0 = 4. * pi * 10e-7  # N A^-2
# Vacuum Permittivity (epsilon_0)
epsilon_0 = 1. / (mu_0 * c ** 2)  # F m^-1
# Coulomb's Constant (k_e)
k_e = 1. / (4 * pi * epsilon_0)  # m F^-1

# OTHER USEFUL QUANTITIES

# Specific heat capacity of water
shc_water = 4.186e3  # J kg^-1 K^-1

# PREFIXES

atto = 1e-18
femto = 1e-15
pico = 1e-12
nano = 1e-9
micro = 1e-6
milli = 1e-3
centi = 1e-2
deca = 10
hecto = 1e2
kilo = 1e3
mega = 1e6
giga = 1e9
tera = 1e12
peta = 1e15
exa = 10e18

# ACCELERATION (metres/second^2 [m/s^2])

# Average acceleration due to gravity at sea level (on Earth)
g = 9.80665

acceleration_units = {"m/s^2": 1., "g": g}


def acceleration_to_m_s_2(acc: "float", units="g"):
    if units not in acceleration_units:
        raise ValueError('Unrecognised unit.')

    factor = acceleration_units[units]

    return acc * factor


def acceleration_from_m_s_2(acc: "float", units="g"):
    if units not in acceleration_units:
        raise ValueError('Unrecognised unit.')

    factor = acceleration_units[units]

    return acc / factor


def acceleration_to_acceleration(acc: "float", frm: "str", to: "str"):
    if frm not in acceleration_units:
        raise ValueError(frm + ' is an unrecognised unit.')
    if to not in acceleration_units:
        raise ValueError(to + ' is an unrecognised unit.')

    acc = acceleration_to_m_s_2(acc, frm)
    return acceleration_from_m_s_2(acc, to)


# ANGLE (in radians [rad])

# Circle
circle = 2 * pi
# Degrees (deg)
degree = pi / 180.
# Minutes of arc (arcmin)
arcmin = degree / 60.
# Seconds of arc (arcsec)
arcsec = arcmin / 60.

# Right ascension hours
ra_hr = pi / 12.
# Right ascension minutes
ra_min = ra_hr / 60.
# Right ascension seconds
ra_sec = ra_min / 60.

angle_units = {"rad": 1., "radians": 1., "circle": circle, "deg": degree, "degree": degree, "degrees": degree,
               "arcmin": arcmin,
               "arcsec": arcsec, "ra_hr": ra_hr, "ra_min": ra_min, "ra_sec": ra_sec}


def angle_to_radians(angle: "float", units: "str" = "degree"):
    if units not in angle_units:
        raise ValueError('Unrecognised unit.')

    factor = angle_units[units]

    return angle * factor


def angle_from_radians(angle: "float", units: "str" = "degree"):
    if units not in angle_units:
        raise ValueError('Unrecognised unit.')

    factor = angle_units[units]

    return angle / factor


def angle_to_angle(angle: "float", frm: "str", to: "str"):
    if frm not in angle_units:
        raise ValueError(frm + ' is an unrecognised unit.')
    if to not in angle_units:
        raise ValueError(to + ' is an unrecognised unit.')

    angle = angle_to_radians(angle, frm)
    return angle_from_radians(angle, to)


def angle_arc_to_decimal(deg: "float", mins: "float", secs: "float", radians=False):
    """
    Converts a measurement in degrees, arcminutes, arcseconds to a decimal fraction of degrees.
    :param deg:
    :param mins:
    :param secs:
    :param radians: If True, converts the result into radians.
    :return:
    """

    angle = float(deg) + (1. / 60.) * float(mins) + (1. / 3600.) * float(secs)
    if radians:
        angle = angle_to_radians(angle, units="degrees")

    return angle


def angle_ra_to_radians(hrs: "float", mins: "float", secs: "float"):
    """
    Converts a measurement of right ascension in hours, minutes, seconds to radians
    :param hrs:
    :param mins:
    :param secs:
    :return:
    """

    return angle_to_radians(hrs, "ra_hr") + angle_to_radians(mins, "ra_min") + angle_to_radians(secs, "ra_sec")


# ANGULAR VELOCITY (in radians/second [rad/s])

# Revolutions / minute (rpm)
rpm = circle / 60.
ang_vel_units = {"radians_s": 1., "rpm": rpm}


def ang_vel_to_radians_s(ang_vel, units='rpm'):
    if units not in ang_vel_units:
        raise ValueError('Unrecognised unit.')

    factor = ang_vel_units[units]

    return ang_vel * factor


# ELECTRIC CHARGE (in Coulombs [C])

# Elementary charge (e)
e = 1.602176565e-19

# ELECTRIC CURRENT (in Amperes [A], C/s)


# ENERGY (in Joules [J], N m)

# Electron Volt (eV)
eV = 1.602176565e-19
# Calorie
cal = 4.184
# Kilocalorie / food calorie
Cal = kilo * cal

# FORCE (in Newtons [N])

# pound-force (lbf)
lbf = 4.4482216152605

# LENGTH (in metres [m])

# Astronomical Unit (AU)
AU = 149597870700.
# Light year (ly)
ly = 9460730472580800.
# Parsec (pc)
pc = 3.0857e16

# US inch (in, ")
inch = 25.4e-3
# US pica (P̸)
pica = inch / 6.
# US point (p)
p = pica / 12.
# US foot (ft, ')
ft = 12 * inch
# US yard (yd)
yd = 3 * ft
# US mile (mi)
mi = 5280 * ft

# US link (li)
li = (33. / 50.) * ft
# US survey foot (survey ft)
survey_ft = 1200. / 3937.
# US rod (rd)
rd = 25 * li
# US chain (ch)
ch = 4 * rd
# US furlong (fur)
fur = 10 * ch
# US survey mile (survey mi)
survey_mi = 8 * fur
# US league (lea)
lea = 3 * survey_mi

# fathom (ftm)
ftm = 2 * yd
# cable (cb)
cb = 120 * ftm
# nautical mile (nmi)
nmi = 1.852 * kilo

# Earth radius
R_E = 6.371e3

length_units = {'m': 1., 'AU': AU, 'ly': ly, 'parsec': pc, 'pc': pc}


def length_to_metre(length, units='AU'):
    if units not in length_units:
        raise ValueError('Unrecognised unit.')

    factor = length_units[units]

    return length * factor


def length_from_metre(length, units='AU'):
    if units not in length_units:
        raise ValueError('Unrecognised unit.')

    factor = length_units[units]

    return length / factor


def length_to_length(length, frm='pc', to='ly'):
    if frm not in length_units:
        raise ValueError(frm + ' is an unrecognised unit.')
    if to not in length_units:
        raise ValueError(to + ' is an unrecognised unit.')

    length = length_to_metre(length, frm)
    return length_from_metre(length, to)


# AREA (metres^2 [m^2])

# US square survey foor (ft^2)
sq_ft = survey_ft ** 2
# US square chain (ch^2)
sq_ch = ch ** 2
# US acre
acre = 10 * sq_ch
# US section
section = 640 * acre
# US survey township (twp)
twp = 36 * section

# VOLUME (litres [L])

# US cubic inch (cu in)
cu_inch = inch ** 3
# US cubic foot (cu ft)
cu_ft = ft ** 3
# US cubic yard (cu yd)
cu_yd = yd ** 3
# acre-foot (acre ft)
acre_ft = 43560 * cu_ft

# US minim (min)
minim = 61.611519921875e-6
# US fluid dram (fl dr)
fl_dr = 60 * minim
# US teaspoon (tsp)
tsp = 80 * minim
# US tablespoon (Tbsp)
Tbsp = 3 * tsp
# US fluid ounce
fl_oz = 2 * Tbsp
# US shot (jig)
jig = 3 * Tbsp
# US gill (gi)
gi = 4 * fl_oz
# US cup (cp)
cp = 2 * gi
# US pint (pt)
pt = 2 * cp
# US quart (qt)
qt = 2 * pt
# US gallon (gal)
gal = 4 * qt

# MASS (in kilograms kg)

# electron mass
m_e = 9.10938291e-31
# neutron mass
m_n = 1.674927351e-27
# Proton mass
m_p = 1.672621777e-27

# Earth mass
M_E = 5.9722e24
# Jupiter mass
M_J = 1.898e27
# Solar mass
M_sol = 1.98855e30

# US grain (gr)
gr = 64.79891e-3
# US dram (dr)
dr = (875. / 32.) * gr
# US ounce (oz)
oz = 16 * dr
# US pound (lb)
lb = 16 * oz
# US hundredweight (cwt)
cwt = 100 * lb
# US long hundredweight
cwt_long = 112 * lb
# US ton
ton = 20 * cwt
# US long ton
ton_long = 20 * cwt_long

mass_units = {"kg": 1., "M_E": M_E, "M_J": M_J, "M_sol": M_sol}


def mass_to_kg(mass, units='M_E'):
    """
    Converts another mass to kilograms
    :param mass:
    :param units:
    :return:
    """

    if units not in mass_units:
        raise ValueError('Unrecognised unit.')

    factor = mass_units[units]

    return mass * factor


def mass_from_kg(mass, units='M_E'):
    """
    Converts a kilogram mass to another unit.
    :param mass:
    :param units:
    :return:
    """
    if units not in mass_units:
        raise ValueError('Unrecognised unit.')

    factor = mass_units[units]

    return mass / factor


def mass_to_mass(mass, frm='M_E', to='M_J'):
    if frm not in mass_units:
        raise ValueError(frm + ' is an unrecognised unit.')
    if to not in mass_units:
        raise ValueError(to + ' is an unrecognised unit.')

    mass = mass_to_kg(mass, frm)
    return mass_from_kg(mass, to)


# MASS DENSITY (kilograms / metres^3 [kg/m^3])

# Density of air
rho_A = 1.2922
# Density of water
rho_W = 1e3

# SPECIFIC FLUX (Watts / metres^2 Hertz [W m^-2 Hz^-1)])

# Jansky (Jy)
janksy = 10e-26


# TEMPERATURE (Kelvin [K])
# TODO: Farenheit to Kelvin, Kelvin to Farenheit

def temperature_kelvin_to_celsius(temperature: "float"):
    return temperature - 273.15


def temperature_celsius_to_kelvin(temperature: "float"):
    return temperature + 273.15


# TIME (in s)

# Minute (min)
minute = 60.
# Hour (hr)
hr = 60. * minute
# Day
day = 24. * hr
# Year (yr) - This is one calender year, 365 days precisely
yr = 365. * day
# Julian year
yr_Julian = 365.25 * day
# Gregorian year
yr_Gregorian = 365.3435 * day

# Orbital year
# This is one orbital year, the length of time the Earth takes to orbit the sun; it is slightly longer than a calender
# year, hence leap years.
yr_orbital = 1.00001742096 * yr

time_units = {"s": 1., "yr": yr}


def time_from_sec(time, units='yr'):
    if units not in time_units:
        raise ValueError('Unrecognised unit.')

    factor = time_units[units]

    return time / factor


def time_to_sec(time, units='yr'):
    if units not in time_units:
        raise ValueError('Unrecognised unit.')

    factor = time_units[units]

    return time * factor


# VELOCITY (in metres/second [m/s])

# Speed of sound in air
v_A = 343.2

# kilometres per hour (kph)
kph = kilo / hr

# US miles per hour (mph)
mph = mi / hr

vel_units = {"m_s": 1., "c": c}


def velocity_from_m_s(v, units='c'):
    if units not in vel_units:
        raise ValueError('Unrecognised unit.')

    factor = vel_units[units]

    return v / factor


def velocity_to_m_s(v, units='c'):
    if units not in vel_units:
        raise ValueError('Unrecognised unit.')

    factor = vel_units[units]

    return v * factor
