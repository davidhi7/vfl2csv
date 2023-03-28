from vfl2csv_forms import config
from vfl2csv_gui.TextMap import TextMap
from vfl2csv_gui.interfaces.ConversionGuiConfig import ConversionGuiConfig

forms_gui_config = ConversionGuiConfig(text_map=TextMap({
    'window-title': 'Formular erstellen',
    'content-title': 'Formular erstellen',
    'input-files': 'Dateien auswählen',
    'input-directory': 'Verzeichnis auswählen',
    'filedialog-input-single-file': 'Metadaten-Datei auswählen',
    'filedialog-input-single-file-filter': f'Metadaten ({config["Input"]["metadata_search_pattern"]});;Alle Dateien (*)',
    'filedialog-input-dictionary': 'Metadaten-Verzeichnis auswählen',
    'no-files-selected': 'Es sind keine Versuchsflächen ausgewählt.',
    'n-files-selected': '{} Versuchsflächen ausgewählt:',
    'error-no-files-selected': 'Es sind keine Versuchsflächen ausgewählt!',
    'filedialog-output': 'Dateispeicherort',
    'filedialog-output-filter': 'Excel-Datei (*.xlsx)',
    'input-no-files-found': 'Keine Versuchsflächen gefunden!',
    'input-error-reading-file': 'Fehler beim Laden der Datei {}',
    'input-error-general': 'Fehler beim Laden der Dateien',
    'convert': 'Formular erstellen',
    'conversion-error-title': 'Fehler beim Erstellen der Datei',
    'done': 'Formular erstellt',
    'list-headers': ['Versuch', 'Parzelle']
}), output_is_file=True, output_file_extension='xlsx')
