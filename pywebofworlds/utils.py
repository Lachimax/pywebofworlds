from typing import List, Union
import math as m
import astropy.units as units


# TODO: Standardise handling of CSV files using built in csv reader/writer

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


def leading_zeroes(n, digits=2):
    """
    Converts n into a string, with front zero padding to the number of digits specified.
    :param n: Number to be padded.
    :param digits: Number of digits to pad to.
    :return:
    """

    negative = False

    if n < 10 ** digits:
        # Get the number of digits in the number.
        if n == 0:
            n_digits = 1
        else:
            if n < 0:
                lead = "-"
                n = -n
            else:
                lead = ""
            n_digits = int(math.log10(n)) + 1
        # Calculate the number of leading zeroes needed.
        zeroes = digits - n_digits
        # Append that number of zeroes
        for i in range(zeroes):
            lead = lead + "0"

        return lead + str(n)

    else:
        return str(n)


def sanitise_file_ext(path: str, ext: str = '.csv'):
    """
    If the path does not end in the desired extension, appends it.
    :param path: Path to check.
    :param ext: Extension to check for and append if not found.
    :return: Appended path.
    """
    if ext[0] != '.':
        ext = '.' + ext
    if path[-len(ext):] != ext:
        path += ext
    return path


def write_wow_csv(path: str, header: str, names: List[str], rows: List[str]):
    """
    Writes a .csv file with a header specifying the appropriate data type and other information.
    :param path: Path to file; existing files will be overwritten.
    :param header: Header to write.
    :param names: List of column names for the file.
    :param rows: List of rows, as strings.
    :return:
    """
    path = sanitise_file_ext(path=path, ext='.csv')
    name_string = ''
    for name in names:
        name_string += str(name) + ','
    name_string = name_string[:-1] + '\n'
    with open(path, 'w') as file:
        file.writelines(header + '\n')
        file.writelines(name_string)
        for row in rows:
            file.writelines(row + '\n')


def read_wow_csv(path: str, dtype: list = None):
    """
    Reads a .csv file written by write_wow_csv().
    :param path: Path to file.
    :param dtype: List of data types corresponding to the csv columns, to which this method will attempt to cast them.
    :return: tuple of file header, column names and table rows, all as lists.
    """
    path = sanitise_file_ext(path=path, ext='.csv')
    with open(path, 'r') as file:
        header = split_csv_row(file.readline())
        names = split_csv_row(file.readline(), remove=':')
        rows = []
        row = split_csv_row(file.readline())
        while row:
            row = format_csv_row(row, dtype)
            rows.append(row)
            row = split_csv_row(file.readline())
    return header, names, rows


def format_csv_row(row: List[str], dtype: Union[List[type], type] = None):
    """
    Takes a list of strings and returns it as a list cast to the specified data types.
    :param row: List of strings to format.
    :param dtype: List of datatypes to attempt casting to, or else a single type to cast to.
    :return:
    """
    if dtype is None:
        dtype = str
    if type(dtype) is type:
        dtypes = []
        for i in range(len(row)):
            dtypes.append(dtype)
    elif type(dtype) is list:
        dtypes = dtype
    else:
        raise TypeError('dtype must be list or type.')
    while len(dtypes) < len(row):
        dtypes.append(str)
    while len(dtypes) > len(row):
        dtypes.pop(-1)

    new_row = []

    for i, cell in enumerate(row):
        if dtypes[i] is bool:
            if cell == 'FALSE' or cell == 'False':
                new_row.append(False)
            else:
                new_row.append(True)
        else:
            new_row.append(dtypes[i](cell))
    return new_row


def split_csv_row(row: str, remove: str = None):
    """
    Splits a row from a csv file into its component cells, and returns it as a list of strings.
    :param row: The csv row to be split.
    :param remove: If specified, this string will be removed from each cell.
    :return:
    """
    return split_string(string=row, delimiter=',', remove=remove)


def split_string(string: str, delimiter: str = ';', remove: str = None):
    strings = []
    string_piece = ''
    for char in string:
        if char == delimiter or char == '\n':
            if remove is not None:
                string = string.replace(remove, '')
            strings.append(string_piece)
            string_piece = ''
        else:
            string_piece += char
    return strings


def check_quantity(
        number: Union[float, int, units.Quantity],
        unit: units.Unit,
        allow_mismatch: bool = True,
        enforce_equivalency: bool = True,
        convert: bool = False
):
    """
    If the passed number is not a Quantity, turns it into one with the passed unit. If it is already a Quantity,
    checks the unit; if the unit is compatible with the passed unit, the quantity is returned unchanged (unless convert
    is True).

    :param number: Quantity (or not) to check.
    :param unit: Unit to check for.
    :param allow_mismatch: If `False`, even compatible units will not be allowed.
    :param enforce_equivalency: If `True`, and if `allow_mismatch` is True, a `units.UnitsError` will be raised if the
        `number` has units that are not equivalent to `unit`.
        That is, set this (and `allow_mismatch`) to `True` if you want to ensure `number` has the same
        dimensionality as `unit`, but not necessarily the same units. Savvy?
    :param convert: If `True`, convert compatible `Quantity` to units `unit`.
    :return:
    """
    if number is None:
        return None
    if not isinstance(number, units.Quantity):  # and number is not None:
        number *= unit
    elif number.unit != unit:
        if not allow_mismatch:
            raise units.UnitsError(
                f"This is already a Quantity, but with units {number.unit}; units {unit} were specified.")
        elif enforce_equivalency and not (number.unit.is_equivalent(unit)):
            raise units.UnitsError(
                f"This number is already a Quantity, but with incompatible units ({number.unit}); units {unit} were specified.")
        elif convert:
            number = number.to(unit)
    return number
