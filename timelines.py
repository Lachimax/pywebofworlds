import numpy as np
from typing import Union


class DateSystem:
    def __init__(self, year: float, year0: float, months: Union[list, dict] = None, month_lengths: list = None,
                 summer_start: float = 11. / 12., max_year: int = 10000, min_year: int = -10000):
        """

        :param year: Year length of the date system, in hours
        :param year0: Year (Gregorian date) of the date system's year 0.
        :param months: list of month names for your system. If a dict, keys should be month names and values should be
            month lengths, in days; this will override month_lengths.
        :param month_lengths: list of month lengths, in days, to correspond to the names.
        :param summer_start: fraction through the year at which summer begins.
        :param max_year: maximum year.
        :param min_year: minimum year.
        """
        self.year = year
        self.year0 = year0
        if type(months) is dict:
            self.months = list(months.keys())
            self.month_lengths = list(months.values())
        else:
            self.months = months
            self.month_lengths = month_lengths

        self.summer_start = summer_start
        self.max_year = max_year
        self.min_year = min_year

    def days_in_year(self):
        return sum(self.month_lengths)

    def date_of_nth_day(self, n):
        return self.days_of_year()[n - 1]

    def days_of_year(self):
        """
        Generate list of all days in the year.
        :return:
        """
        days = []
        for i, month in enumerate(self.months):
            for j in range(self.month_lengths[i]):
                days.append(Date(year=None, month=i + 1, day=j + 1, system=self))
        return days

    def equivalent_date(self, date: Union['Date', str], other: Union['DateSystem', str] = 'Gregorian'):
        """
        Gives you the equivalent date for the time of year in another system. Does not currently take seasons into account.
        :param other:
        :param date:
        :return:

        """
        # If 'other' is a string, attempt to use that to set the date system from the available defaults.
        other = check_available(other)

        # If 'date' is a string, convert it to a Date object.
        if type(date) is str:
            date = Date(string=date)

        # Divide the date's position in the year by the number of days in a year, then multiply by the number of days in
        # other system's year to get the equivalent position.
        position = other.days_in_year() * date.day_of_year() / self.days_in_year()
        return other.days_of_year()[int(np.round(position))]


# TODO: Decimal year to date conversion (nontrivial with negative dates - have to flip)
# TODO: Named month format
class Date:
    def __init__(self, string: str = None, year: int = None, month: int = None, day: int = None, time=None,
                 system: Union[DateSystem, str] = 'Gregorian'):
        """

        :param string: Date in string format. Overrides year, month, and day.
        :param year:
        :param month:
        :param day:
        :param time:
        :param system: DateSystem to use. If a string is passed, attempts to match it to the defaults in
            availableSystems.
        """

        # If 'system' is a string, attempt to use that to set the date system from the available defaults.
        self.system = check_available(system)

        self.max_days = self.system.month_lengths

        if string is not None:
            self.str_to_date(date=string)
        else:
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

    def __str__(self):
        return self.show(fmt='yyyy-mm-dd')

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

    def str_to_date(self, date: str, fmt: str = 'yyyy-mm-dd'):
        if fmt == 'yyyy-mm-dd':
            self.year = int(date[0:4])
            self.month = int(date[5:7])
            self.day = int(date[8:])

    def day_of_year(self):
        """
        Calculate which numbered day of the year this is.
        :return:
        """
        days = 0
        for i in range(self.month - 1):
            days += self.system.month_lengths[i]
        days += self.day
        return days

    def rand_date(self):
        self.set_year(np.random.randint(self.system.min_year, self.system.max_year + 1))

        self.set_month(np.random.randint(1, 13))

        max_day = self.max_days[self.month - 1]

        self.set_day(np.random.randint(1, max_day + 1))

    # TODO: Adapt this to use your order-of-magnitude code for adding leading zeroes.
    def show(self, fmt='yyyy-mm-dd'):
        available_formats = ['yyyy-mm-dd', 'Words']

        if fmt not in available_formats:
            raise ValueError('Date format not recognised')

        if fmt == 'yyyy-mm-dd':
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

        elif fmt == 'Words':
            return self.month_name + ' ' + str(self.day) + ', ' + str(self.year)


# Date systems in my universe:
gregorian = DateSystem(year=8766.152712096, year0=0,
                       months=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                               'October', 'November', 'December'],
                       month_lengths=[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

# conjugus = DateSystem(year=21343.3036, year0=)
pendant = DateSystem(year=8640, year0=1793.84,
                     months=['Torgien', 'Lodda', 'Rewis', 'Corper', 'Zholdan', 'Affelkate', 'Sherrey', 'Vuzhord'],
                     month_lengths=[30, 30, 30, 30, 30, 30, 30, 30], summer_start=11. / 12.)
provectus = DateSystem(year=8766, year0=-999988290.59)
rachara = DateSystem(year=168062.878, year0=-2026.71)
semartol = DateSystem(year=22070.5, year0=-3585.07)

availableSystems = {'Earth': gregorian, 'Gregorian': gregorian, 'Pendant': pendant, 'Ancient': provectus,
                    'Provectus': provectus, 'Rachara': rachara, 'Semartol': semartol}


def check_available(system: Union[str, DateSystem]):
    # If 'system' is a string, attempt to use that to set the date system from the available defaults.
    if type(system) is str:
        if system in availableSystems:
            return availableSystems[system]
        else:
            raise ValueError('Date system not recognised')
    elif type(system) is DateSystem:
        return system


def str_to_date(string: str, fmt: str = 'yyyy-mm-dd'):
    return Date().str_to_date(string, fmt)


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
    For obtaining Year 0 of system 1 in system 2, knowing Year 0 of system 2 in system 1
    :param year0:
    :param yr_old:
    :param yr_new:
    :return:
    """
    return -year0 * (yr_new / yr_old)


def convert_date_sys(t_old, old_sys: Union[str, DateSystem] = 'Gregorian', new_sys: Union[str, DateSystem] = 'Pendant'):
    new_sys = check_available(new_sys)
    old_sys = check_available(old_sys)

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


def leading_zeroes(n, digits=2):
