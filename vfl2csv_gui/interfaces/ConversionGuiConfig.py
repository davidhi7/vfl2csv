from dataclasses import dataclass
from typing import Optional

from vfl2csv_gui.TextMap import TextMap


@dataclass
class ConversionGuiConfig:
    text_map: TextMap
    output_is_file: bool
    output_file_extension: Optional[str] = None
