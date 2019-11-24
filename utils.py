from typing import List, Union


def sanitise_file_ext(path: str, ext: str = '.csv'):
    """
    If the path does not end in the desired extension, appends it.
    :param path: Path to check.
    :param ext: Extension to check for and append if not found.
    :return: Appened path.
    """
    if ext[0] != '.':
        ext = '.' + ext
    if path[-len(ext):] != ext:
        path += ext
    return path


def write_wow_csv(path: str, header: str, names: list, rows: List[str]):
    """
    Writes a .csv file with a header specifying the appropriate data type and other information.
    :param path:
    :param header:
    :param names:
    :param rows:
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
    path = sanitise_file_ext(path=path, ext='.csv')
    with open(path, 'r') as file:
        header = split_csv_row(file.readline())
        names = split_csv_row(file.readline())
        rows = []
        row = split_csv_row(file.readline())
        while row:
            row = format_csv_row(row, dtype)
            rows.append(row)
            row = split_csv_row(file.readline())
    return header, names, rows


def format_csv_row(row: List[str], dtype: Union[List[type], type] = None):
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

    if len(dtypes) != len(row):
        raise ValueError(f'If provided as a list, dtypes must be of equal length to row ({len(dtypes)} != {len(row)}).')

    new_row = []

    for i, cell in enumerate(row):
        if dtypes[i] is bool:
            if cell == 'FALSE':
                new_row[i] = False
            else:
                new_row[i] = True
        else:
            new_row[i] = dtypes[i](cell)
    return new_row


def split_csv_row(row: str):
    cells = []
    cell = ''
    for char in row:
        if char == ',' or char == '\n':
            cells.append(cell)
            cell = ''
        else:
            cell += char
    return cells
