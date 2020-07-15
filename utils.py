from typing import List, Union
import math as m


def leading_zeroes(n, digits=2):
    """
    Converts n into a string, with front zero padding to the number of digits specified.
    :param n: Number to be padded.
    :param digits: Number of digits to pad to.
    :return:
    """
    if n < 10 ** digits:
        # Get the number of digits in the number.
        if n == 0:
            n_digits = 1
        else:
            n_digits = int(m.log10(n)) + 1
        # Calculate the number of leading zeroes needed.
        zeroes = digits - n_digits
        # Append that number of zeroes
        lead = ""
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
    cells = []
    cell = ''
    for char in row:
        if char == ',' or char == '\n':
            if remove is not None:
                cell = cell.replace(remove, '')
            cells.append(cell)
            cell = ''
        else:
            cell += char
    return cells
