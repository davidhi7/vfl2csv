from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import NamedStyle, Font, Alignment, PatternFill

metadata_keys = NamedStyle('metadata-keys',
                           font=Font(bold=True, name='Calibri', size=12),
                           alignment=Alignment(horizontal='right')
                           )

metadata_values = NamedStyle('metadata-values', Font(name='Calibri', size=12))

table_head = NamedStyle('table-head',
                        font=Font(bold=True, name='Calibri', size=12),
                        alignment=Alignment(horizontal='center')
                        )

table_body_text = NamedStyle('table-body text', font=Font(name='Calibri', size=12))
table_body_integer = NamedStyle('table-body integer', font=Font(name='Calibri', size=12), number_format='0')
table_body_rational = NamedStyle('table-body rational', font=Font(name='Calibri', size=12), number_format='0.0')

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
