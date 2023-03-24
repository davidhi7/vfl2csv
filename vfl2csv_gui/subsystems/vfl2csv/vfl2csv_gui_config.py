from vfl2csv import setup
from vfl2csv_gui.TextMap import TextMap
from vfl2csv_gui.interfaces.ConversionGuiConfig import ConversionGuiConfig

vfl2csv_gui_config = ConversionGuiConfig(text_map=TextMap({
    'window-title': 'Dateien konvertieren',
    'content-title': 'Dateien konvertieren',
    'filedialog-input-single-file': 'Eingabedateien auswählen',
    'filedialog-input-single-file-filter':
        f'{setup.config["Input"]["input_format"]}-Dateien (*.{setup.config["Input"]["input_file_extension"]});;Alle Dateien (*)',
    'filedialog-input-dictionary': 'Eingabeverzeichnis auswählen',
    'no-files-selected': 'Es sind keine Eingabedateien ausgewählt.',
    'n-files-selected': '{} Dateien ausgewählt:',
    'error-no-files-selected': 'Es sind keine Eingabedateien ausgewählt!',
    'filedialog-output': 'Zielverzeichnis',
    'input-no-files-found': 'Keine Eingabedateien gefunden!',
    'input-error-reading-file': 'Fehler beim Laden der Datei {}',
    'input-error-general': 'Fehler beim Laden der Dateien',
    'convert': 'Dateien konvertieren',
    'conversion-error-title': 'Fehler beim Konvertieren der Dateien',
    'done': 'Dateien konvertiert',
    'list-headers': ['Datei']
}), output_is_file=False)
