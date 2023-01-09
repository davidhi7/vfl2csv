import logging
import traceback
from pathlib import Path

from PySide6.QtCore import Slot, Qt, Signal, QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QLabel, QVBoxLayout, QMessageBox, \
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from openpyxl.reader.excel import load_workbook
from pandas import ExcelWriter

from vfl2csv_base.input.TrialSite import TrialSite
from .qt_util import QHLine
from ..excel.styles import register
from ..trial_site_conversion import run

logger = logging.getLogger(__name__)


class InputHandler(QWidget):
    """
    Signal that is emitted if a success needs to be emitted. The sole attribute is a message string.
    """
    notification_success = Signal(str)

    """
    Signal that is emitted if a warning needs to be emitted. The sole attribute is a message string.
    """
    notification_warning = Signal(str)

    """
    Signal that is emitted if an error occurs. The attributes are a message string, an exception object and a 
    traceback string.
    """
    notification_error = Signal(str, Exception, str)

    def __init__(self):
        super().__init__()

        self.trial_sites = []

        single_file_input = QPushButton('Datei(en) auswählen')
        single_file_input.clicked.connect(self.single_file_input)
        directory_input = QPushButton('Verzeichnis auswählen')
        directory_input.clicked.connect(self.directory_input)
        input_separator = QLabel('oder')
        input_separator.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.addWidget(single_file_input)
        button_layout.addWidget(input_separator)
        button_layout.addWidget(directory_input)

        main_layout = QVBoxLayout()
        self.status_label = QLabel()

        self.status_table = QTableWidget(0, 2)
        self.status_table.setVisible(False)
        self.status_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.run_button = QPushButton('Formular erzeugen')
        self.run_button.clicked.connect(self.create)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(QHLine())
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.status_table)
        main_layout.addWidget(QHLine())
        main_layout.addWidget(self.run_button)

        self.setLayout(main_layout)

        self.notification_success.connect(self.notify_success)
        self.notification_warning.connect(self.notify_warning)
        self.notification_error.connect(self.notify_error)

        self.update_trial_site_list()

    @Slot()
    def single_file_input(self):
        self.trial_sites.clear()
        files_input = QFileDialog.getOpenFileNames(parent=self,
                                                   caption='Metadaten-Datei auswälen',
                                                   filter='Metadaten (*.txt);;Alle Dateien (*)'
                                                   )
        self.handle_input(files_input[0])
        self.update_trial_site_list()

    @Slot()
    def directory_input(self):
        self.trial_sites.clear()
        files_input = QFileDialog.getExistingDirectory(parent=self,
                                                       caption='Metadaten-Verzeichnis auswählen',
                                                       options=QFileDialog.ShowDirsOnly
                                                       )
        # QFileDialog.getExistingDirectory returns only the selected path, no other nested values
        self.handle_input(files_input)
        self.update_trial_site_list()

    def handle_input(self, input_paths: str | Path | list[str]):
        if isinstance(input_paths, list):
            for path in input_paths:
                self.handle_input(path)
            return
        path = Path(input_paths)
        if not path.exists():
            self.notification_warning.emit(f'Datei oder Verzeichnis {path} existiert nicht')
            return
        if path.is_dir():
            for content in path.glob('*.txt'):
                self.handle_input(content)
            return

        try:
            path = Path(input_paths)
            self.trial_sites.append(TrialSite.from_metadata_file(path))
        except ValueError as err:
            logger.error(f'Error during reading file {input_paths}', exc_info=True)
            self.notification_error.emit(f'Fehler beim Lesen der Datei {input_paths}', err, traceback.format_exc())
            self.trial_sites.clear()

    def update_trial_site_list(self):
        trial_site_count = len(self.trial_sites)
        if trial_site_count == 0:
            self.status_label.setText('Es sind gegenwärtig keine Versuchsflächen ausgewählt.')
            self.status_table.setVisible(False)

            self.run_button.setEnabled(False)
        else:
            self.status_label.setText(f'Es sind folgende {trial_site_count} Versuchsflächen ausgewählt:')

            self.status_table.clear()
            self.status_table.setVisible(True)
            self.status_table.setHorizontalHeaderLabels(('Versuch', 'Parzelle'))
            self.status_table.setRowCount(trial_site_count)
            for index, trial_site in enumerate(self.trial_sites):
                item_trial = QTableWidgetItem(trial_site.metadata['Versuch'])
                self.status_table.setItem(index, 0, item_trial)
                self.status_table.setItem(index, 1, QTableWidgetItem(trial_site.metadata['Parzelle']))
            self.run_button.setEnabled(True)
            # TODO: adjust column heights so this actually adapts to different row counts
            self.status_table.setMinimumSize(self.getQTableWidgetSize())
            self.status_table.setMaximumSize(self.getQTableWidgetSize())

    """
    https://stackoverflow.com/questions/41542934/remove-scrollbar-to-show-full-table
    """

    def getQTableWidgetSize(self):
        w = self.status_table.verticalHeader().width() + 4  # +4 seems to be needed
        for i in range(self.status_table.columnCount()):
            w += self.status_table.columnWidth(i)  # seems to include gridline (on my machine)
        h = self.status_table.horizontalHeader().height() + 4
        for i in range(self.status_table.rowCount()):
            h += self.status_table.rowHeight(i)
        return QSize(w, h)

    @Slot()
    def notify_success(self, message: str):
        self.notification(message, None, None, icon=QMessageBox.Icon.Information)

    @Slot()
    def notify_warning(self, message: str):
        self.notification(message, None, None, icon=QMessageBox.Icon.Warning)

    @Slot()
    def notify_error(self, message: str, exception: Exception, traceback: str):
        self.notification(self,
                          message,
                          f'{type(exception).__name__}: {str(exception)}',
                          traceback,
                          QMessageBox.Icon.Critical
                          )

    def notification(self, text: str, informative_text: str | None, detailed_text: str | None, icon: QMessageBox.Icon):
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon or QMessageBox.Icon.NoIcon)
        msg_box.setText(text)
        if informative_text is not None:
            msg_box.setInformativeText(informative_text)
        if detailed_text is not None:
            msg_box.setDetailedText(detailed_text)
        msg_box.exec()

    @Slot()
    def create(self):
        output_path = QFileDialog.getSaveFileName(self,
                                                  caption='Dateispeicherort',
                                                  dir=str(Path.home()),
                                                  filter='Excel-Datei (*.xlsx)'
                                                  )[0]
        if not output_path.endswith('.xlsx'):
            output_path += '.xlsx'

        # TODO remove and replace with better solution
        trial_site_forms = []
        with ExcelWriter(Path(output_path)) as writer:
            for trial_site in self.trial_sites:
                trial_site_form = run(trial_site, Path(output_path))
                trial_site_form.init(writer)
                trial_site_forms.append(trial_site_form)

        workbook = load_workbook(output_path)
        register(workbook)
        for trial_site_form in trial_site_forms:
            trial_site_form.create(workbook)

        self.notification_success.emit('Formularerzeugung abgeschlossen')
