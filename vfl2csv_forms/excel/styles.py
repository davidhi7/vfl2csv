from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import NamedStyle, Font, Alignment, PatternFill
from openpyxl.workbook import Workbook

metadata_keys = NamedStyle(name='metadata-keys',
                           font=Font(bold=True, name='Calibri', size=12),
                           alignment=Alignment(horizontal='right')
                           )

metadata_values = NamedStyle(name='metadata-values', font=Font(name='Calibri', size=12))

table_head = NamedStyle(name='table-head',
                        font=Font(bold=True, name='Calibri', size=12),
                        alignment=Alignment(horizontal='center')
                        )

table_body_text = NamedStyle(name='table-body-text', font=Font(name='Calibri', size=12))
table_body_integer = NamedStyle(name='table-body-integer', font=Font(name='Calibri', size=12), number_format='0')
table_body_rational = NamedStyle(name='table-body-rational', font=Font(name='Calibri', size=12), number_format='0.0')

conditional_formatting_greater_than = CellIsRule(
    operator='greaterThan',
    formula=['0'],
    stopIfTrue=True,
    fill=PatternFill(start_color='ccffcc', end_color='ccffcc', fill_type='solid')
)
conditional_formatting_less_than = CellIsRule(
    operator='lessThan',
    formula=['0'],
    stopIfTrue=True,
    fill=PatternFill(start_color='ffcccc', end_color='ffcccc', fill_type='solid')
)


def register(workbook: Workbook):
    for style in (metadata_keys, metadata_values, table_head, table_body_text, table_body_integer, table_body_rational):
        workbook.add_named_style(style)
