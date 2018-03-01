import numpy as np

# TODO: Year conversion system
# TODO: Date system class?

# Returns the index of the desired year in an array of years
class Date:
    # TODO: Implement Pendant system
    def __init__(self, year=None, month=None, day=None, time=None, system='Julian'):

        available_systems = ['Julian']

        if system in available_systems:
            self.system = system
        else:
            raise ValueError('Date system not recognised')

        if self.system == 'Julian':
            # TODO: Account for leap years?
            self.max_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

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

        if self.system == 'Julian':
            if year == 0:
                year = 1

        self.year = year

    def set_month(self, month):

        month = int(month)
        max_month = int()

        month_list = []

        if self.system == 'Julian':
            max_month = 12
            month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                          'October', 'November', 'December']

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
        self.set_year(np.random.randint(1,10000))

        self.set_month(np.random.randint(1, 13))

        max_day = self.max_days[self.month-1]

        self.set_day(np.random.randint(1,max_day+1))

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

def str_to_date(string, format='yyyy-mm-dd'):
    date = Date()
    if format == 'yyyy-mm-dd':
        date.year = int(string[0:4])
        date.month = int(string[5:7])
        date.day = int(string[8:])


def find_year(year, arr):
    """ In an array in which each entry is one year, returns the index of the desired year.

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
