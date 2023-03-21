from vfl2csv_gui.TextMap import TextMap


class ConversionGuiConfig:
    def __init__(self, text_map: TextMap, output_is_file: bool, output_file_extension: str = None):
        self.text_map = text_map
        self.output_is_file = output_is_file
        self.output_file_extension = output_file_extension
