EXCEL_COLUMN_NAMES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def zeroBasedCell(ws, row, column):
    return ws.cell(row=row + 1, column=column + 1)
