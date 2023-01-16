from openpyxl.formatting.rule import CellIsRule, FormulaRule
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
conditional_formatting_equal = CellIsRule(
    operator='equal',
    formula=['0'],
    stopIfTrue=True,
    fill=PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
)
# while Libreoffice does not, Excel, for some reason, applies conditional formatting on cells that get an empty string
# as value. Use this rule without actual formatting being done to bypass this behaviour
conditional_formatting_empty = FormulaRule(
    formula=['LEN(TRIM(J7))=0'],
    stopIfTrue=True,
    # optionally enable light grey background
    # fill=PatternFill(start_color='EEECE1', end_color='EEECE1', fill_type='solid')
)

full_conditional_formatting_list = [
    conditional_formatting_empty,
    conditional_formatting_less_than,
    conditional_formatting_equal,
    conditional_formatting_greater_than
]


def register(workbook: Workbook):
    for style in (metadata_keys, metadata_values, table_head, table_body_text, table_body_integer, table_body_rational):
        workbook.add_named_style(style)
