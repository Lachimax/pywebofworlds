import numpy as np


class DateSystem:
    def __init__(self, year, year0, months=None, month_lengths=None):
        """

        :param year: Year length of the date system, in hours
        :param year0: Year (Gregorian date) of the date system's year 0.
        """
        self.year = year
        self.year0 = year0
        self.months = months
        self.month_lengths = month_lengths


# TODO: Decimal year to date conversion (nontrivial with negative dates - have to flip)
class Date:
    def __init__(self, year=None, month=None, day=None, time=None, system='Gregorian'):

        if system in availableSystems:
            self.system = availableSystems[system]
        else:
            raise ValueError('Date system not recognised')

        self.max_days = self.system.month_lengths

        self.year = int()
        if year is not None:
            self.set_year(year)

        self.month_name = str()
        self.month = int()
        if month is not None:
            self.set_month(month)

        self.day = int()
        if day is not None:
            self.set_day(day)

    def set_year(self, year):

        year = int(year)

        self.year = year

    def set_month(self, month):

        month = int(month)
        max_month = int()

        month_list = self.system.months
        max_month = len(month_list)

        if month > max_month:
            month = max_month
        if month < 1:
            month = 1

        self.month = month
        self.month_name = month_list[month - 1]

    def set_day(self, day):

        if self.month == int():
            raise ValueError('Month must be set first')

        day = int(day)

        max_day = self.max_days[self.month - 1]

        if day < 1:
            day = 1
        if day > max_day:
            day = max_day

        self.day = day

    def str_to_date(self, date, format='yyyy-mm-dd'):
        if format == 'yyyy-mm-dd':
            self.year = int(date[0:4])
            self.month = int(date[5:7])
            self.day = int(date[8:])

    def rand_date(self):
        self.set_year(np.random.randint(1, 10000))

        self.set_month(np.random.randint(1, 13))

        max_day = self.max_days[self.month - 1]

        self.set_day(np.random.randint(1, max_day + 1))

    def show(self, format='yyyy-mm-dd'):
        available_formats = ['yyyy-mm-dd', 'Words']

        if format not in available_formats:
            raise ValueError('Date format not recognised')

        if format == 'yyyy-mm-dd':
            zeros1 = ''
            if abs(self.year) < 1000:
                zeros1 = '0'
            if abs(self.year) < 100:
                zeros1 = '00'
            if abs(self.year) < 10:
                zeros1 = '000'

            zeros2 = ''
            if self.month < 10:
                zeros2 = '0'

            zeros3 = ''
            if self.day < 10:
                zeros3 = '0'

            return zeros1 + str(self.year) + '-' + zeros2 + str(self.month) + '-' + zeros3 + str(self.day)

        elif format == 'Words':
            return self.month_name + ' ' + str(self.day) + ', ' + str(self.year)

    def __str__(self):
        return self.show(format='yyyy-mm-dd')


# Date systems in my universe:
gregorian = DateSystem(year=8766.152712096, year0=0,
                       months=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                               'October', 'November', 'December'],
                       month_lengths=[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

# conjugus = DateSystem(year=21343.3036, year0=)
pendant = DateSystem(year=8640, year0=1793.84,
                     months=['Tolking', 'Rouling', 'Roddah', 'Leuis', 'Appelgaight', 'Kolfir', 'Zhoordin', 'Maarten'],
                     month_lengths=[30, 30, 30, 30, 30, 30, 30, 30])
provectus = DateSystem(year=8766, year0=-999988290.59)
rachara = DateSystem(year=168062.878, year0=-2026.71)
semartol = DateSystem(year=22070.5, year0=-3585.07)

availableSystems = {'Earth': gregorian, 'Gregorian': gregorian, 'Pendant': pendant, 'Ancient': provectus,
                    'Provectus': provectus, 'Rachara': rachara, 'Semartol': semartol}


def str_to_date(string, format='yyyy-mm-dd'):
    date = Date()
    if format == 'yyyy-mm-dd':
        date.year = int(string[0:4])
        date.month = int(string[5:7])
        date.day = int(string[8:])


def find_year(year, arr):
    """ In an array in which each entry is one year, in order, returns the index of the desired year.

    :param year: (int) the desired year
    :param arr: (numpy.array) an array in which each entry is a consecutive year.
    :return: (int) the index of year in arr
    """
    index = year - arr[0]
    return index


def line_func(x1, y1, x2, y2):
    """ Given two points, calculates the gradient and y-intercept of the line joining them.

    :param x1: x-coordinate of first point
    :param y1: y-coordinate of first point
    :param x2: x-coordinate of second point
    :param y2: y-coordinate of second point
    :return: (tuple) Contains the gradient of the line at [0] and the y-intercept at [1], ie (m, b).
    """
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return m, b


def switch_year0(year0, yr_old, yr_new):
    """
    For obtaining Year 0 system 1 in system 2, knowing Year 0 of system 2 in system 1
    :param year0:
    :param yr_old:
    :param yr_new:
    :return:
    """
    return -year0 * (yr_new / yr_old)


# TODO: Change this and other functions to accept DateSystem objects for old_sys and new_sys, as well as strings
def convert_date_sys(t_old, old_sys: 'str' = 'Gregorian', new_sys: 'str' = 'Pendant'):
    new_sys = availableSystems[new_sys]
    old_sys = availableSystems[old_sys]

    # First obtain the Gregorian Year 0 in the current system:
    year0 = switch_year0(year0=old_sys.year0, yr_old=old_sys.year, yr_new=gregorian.year)

    # Use that to convert the date to Gregorian:
    t_old = convert_date(t_old=t_old, year0=year0,
                         yr_old=old_sys.year, yr_new=gregorian.year)

    # Then convert from Gregorian to the target system:
    return convert_date(t_old=t_old, year0=new_sys.year0, yr_old=gregorian.year, yr_new=new_sys.year)


def convert_date(t_old, year0, yr_old, yr_new):
    """

    :param t_old:
    :param year0: Year 0 of the target system with respect to the current one.
    :param yr_old: Year length of the current system, in hours
    :param yr_new: Year length of the target system, in hours
    :return:
    """

    return (t_old - year0) * (yr_old / yr_new)
