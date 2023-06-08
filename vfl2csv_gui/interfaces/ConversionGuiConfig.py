from dataclasses import dataclass, field
from typing import Optional

from vfl2csv_gui.TextMap import TextMap


@dataclass
class ConversionGuiConfig:
    text_map: TextMap
    output_is_file: bool
    output_file_extension: Optional[str] = None
    """
    Checkboxes for settings regarding the conversion process.
    Each string is a key to a value in the TextMap as well as to a boolean in the kwargs provided to the
    ConversionWorker. 
    """
    boolean_options: list[str] = field(default_factory=list)
