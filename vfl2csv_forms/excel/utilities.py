# noinspection SpellCheckingInspection
EXCEL_COLUMN_NAMES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def zero_based_cell(ws, column, row):
    return ws.cell(row=row + 1, column=column + 1)


def zero_based_cell_range(ws, column0, row0, column1, row1):
    return ws[zero_based_cell_range_name(column0, row0, column1, row1)]


def zero_based_cell_name(column, row) -> str:
    return f'{EXCEL_COLUMN_NAMES[column]}{row + 1}'


def zero_based_cell_range_name(column0, row0, column1, row1) -> str:
    return f'{EXCEL_COLUMN_NAMES[column0]}{row0 + 1}:{EXCEL_COLUMN_NAMES[column1]}{row1 + 1}'
