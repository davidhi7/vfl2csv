import math

from openpyxl.cell import Cell

# noinspection SpellCheckingInspection
EXCEL_COLUMN_NAMES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def zero_based_cell(ws, column, row) -> Cell:
    return ws.cell(row=row + 1, column=column + 1)


def zero_based_cell_range(ws, column0, row0, column1, row1):
    return ws[zero_based_cell_range_name(column0, row0, column1, row1)]


def zero_based_cell_name(column, row) -> str:
    return f'{EXCEL_COLUMN_NAMES[column]}{row + 1}'


def zero_based_cell_range_name(column0, row0, column1, row1) -> str:
    return f'{EXCEL_COLUMN_NAMES[column0]}{row0 + 1}:{EXCEL_COLUMN_NAMES[column1]}{row1 + 1}'


def get_character_count(value: str | int | float, decimal_digits: int) -> int:
    if isinstance(value, str):
        return len(value)
    elif isinstance(value, int):
        return int(math.log10(value))
    elif isinstance(value, float):
        # count of digits before the decimal point + the decimal points and count of displayed decimal digits
        return int(math.log10(value)) + 1 + decimal_digits
    else:
        raise ValueError('Given value must be of type `int`, `float` or `string`!')
