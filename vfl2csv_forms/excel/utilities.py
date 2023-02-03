# noinspection SpellCheckingInspection
EXCEL_COLUMN_NAMES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def zero_based_cell(ws, row, column):
    return ws.cell(row=row + 1, column=column + 1)


def zero_based_cell_name(column, row) -> str:
    return f'{EXCEL_COLUMN_NAMES[column + 1]}{row + 1}'
