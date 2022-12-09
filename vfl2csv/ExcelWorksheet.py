import ExcelWorkbook


class ExcelWorksheet:
    def __init__(self, excelworkbook: ExcelWorkbook.ExcelWorkbook, sheetname: str):
        """
        Create Excel worksheet record
        :param excelworkbook: ExcelWorkbook record
        :param sheetname: Target sheet name
        """
        self.workbook = excelworkbook.workbook
        self.workbook_path = excelworkbook.path
        self.name = sheetname
        self.in_mem_file = excelworkbook.in_mem_file
