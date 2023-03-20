from pathlib import Path

from vfl2csv_base import config_factory, default_column_scheme_path, default_column_scheme_json
from vfl2csv_base.ColumnScheme import ColumnScheme
from vfl2csv_gui.TextMap import TextMap

config = config_factory.get_config(Path('config/config_forms.ini'), """[Input]
metadata_search_pattern = *.txt
directory_search_recursively = true

[Output]
excel_sheet_pattern = {versuch}-{parzelle}
""")
column_scheme = ColumnScheme.from_file(path=default_column_scheme_path, template=default_column_scheme_json)
gui_text_map = TextMap({
    'window-title': 'Formular erstellen',
    'content-title': 'Formular erstellen',
    'filedialog-input-single-file': 'Metadaten-Datei auswählen',
    'filedialog-input-single-file-filter': f'Metadaten ({config["Input"]["metadata_search_pattern"]});;Alle Dateien (*)',
    'filedialog-input-dictionary': 'Metadaten-Verzeichnis auswählen',
    'no-files-selected': 'Es sind keine Versuchsflächen ausgewählt.',
    'n-files-selected': '{} Versuchsflächen ausgewählt',
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
})
