from __future__ import annotations

from typing import Union

from openpyxl.styles import NamedStyle

from excel.utilities import zeroBasedCell, EXCEL_COLUMN_NAMES


class FormulaeColumn:

    def __init__(self,
                 is_binary_operator: bool,
                 function: str,
                 label: str,
                 column_arguments: list[Union[int, FormulaeColumn]],
                 style: NamedStyle,
                 conditional_formatting: list
                 ):
        """
        Create a formula column for the output Excel sheet.
        :param is_binary_operator: True if function is a binary operator like +, -, *, /
        :param function: Excel function to apply
        :param label: Title of the column
        :param column_arguments: Columns (0-based numbers) to apply the function on
        """
        if is_binary_operator and len(column_arguments) != 2:
            raise ValueError('Require exactly two output columns when using binary operators!')

        self.is_binary_operator = is_binary_operator
        self.function = function
        self.label = label
        self.column_arguments = column_arguments
        self.style = style
        self.conditional_formatting_rules = conditional_formatting
        self.yielded_column = None

    def insert(self, column: int, rows: list[int], ws):
        """
        Insert the column into the worksheet.
        :param column: Column (0-based) to insert the formulas in
        :param rows: Row (0-based) to fill. Note that the first row will contain the label.
        :param ws: Worksheet
        :returns The number of newly inserted columns (> 1 if this column depended on other instances of this class,
        which were added beforehand).
        """
        # number of columns to shift the parameter 'column' after inserting other columns recursively
        column_shift = 0
        # Worksheet#cell is 1-based, so substract 1 from the column
        zeroBasedCell(ws, rows[0], column).value = self.label
        column_argument_letters = []
        for column_arg in self.column_arguments:
            if isinstance(column_arg, FormulaeColumn):
                if column_arg.yielded_column is None:
                    column_arg.insert(column=column + column_shift, rows=rows, ws=ws)
                    column_shift += 1
                index = column_arg.yielded_column
            else:
                index = column_arg
            column_argument_letters.append(EXCEL_COLUMN_NAMES[index])
        for row in rows[1:]:
            if self.is_binary_operator:
                formula = f'{column_argument_letters[0]}{row + 1} {self.function} {column_argument_letters[1]}{row + 1}'
            else:
                # Separator must be a comma, see https://openpyxl.readthedocs.io/en/stable/usage.html#using-formulae
                column_enumeration = ', '.join(f'{letter}{row + 1}' for letter in column_argument_letters)
                formula = f'{self.function}({column_enumeration})'
            zeroBasedCell(ws, row, column).value = f'=IFERROR({formula}, "")'
            zeroBasedCell(ws, row, column).style = self.style
        column_letter = EXCEL_COLUMN_NAMES[column]
        for conditional_format in self.conditional_formatting_rules:
            ws.conditional_formatting.add(f'{column_letter}{rows[1]}:{column_letter}{rows[-1] + 1}', conditional_format)
        self.yielded_column = column + column_shift
        return column_shift + 1
