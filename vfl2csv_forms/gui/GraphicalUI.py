import logging
import traceback
from pathlib import Path

from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QTableWidget, \
    QAbstractItemView, QHeaderView, QMessageBox, QFileDialog, QTableWidgetItem, QProgressBar

from vfl2csv_forms import config
from vfl2csv_forms.gui.InputHandler import InputHandler
from vfl2csv_forms.gui.QHLine import QHLine

logger = logging.getLogger(__name__)


class GraphicalUI(QWidget):

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.setWindowTitle('Neues Formular erstellen')
        title = QLabel('Formular erstellen')
        title_font = title.font()
        title_font.setPointSize(24)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setMargin(12)

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

        self.status_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_table = QTableWidget(0, 2)
        self.status_table.setVisible(False)
        self.status_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        run_button = QPushButton('Formular erzeugen')
        run_button.clicked.connect(self.create)
        run_button.setStyleSheet('padding: 15px;')

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        self.layout().addWidget(title)
        self.layout().addLayout(button_layout)
        self.layout().addWidget(QHLine())
        self.layout().addWidget(self.status_label)
        self.layout().addWidget(self.status_table)
        self.layout().addWidget(QHLine())
        self.layout().addWidget(run_button)
        self.layout().addWidget(self.progress_bar)

        self.input_handler = InputHandler()
        self.update_input_status()

    @Slot()
    def single_file_input(self):
        self.input_handler.clear()
        self.update_input_status()
        files_input = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Metadaten-Datei auswählen',
            filter=f'Metadaten ({config["Input"].get("metadata_search_pattern")});;Alle Dateien (*)'
        )
        # file dialog likely cancelled
        if not files_input[0]:
            self.update_input_status()
            return
        self.load_input(files_input[0])

    @Slot()
    def directory_input(self):
        self.input_handler.clear()
        directory_input = QFileDialog.getExistingDirectory(
            parent=self,
            caption='Metadaten-Verzeichnis auswählen',
            options=QFileDialog.ShowDirsOnly
        )
        if not directory_input:
            self.update_input_status()
            return
        # QFileDialog.getExistingDirectory returns only the selected path, no other nested values
        self.load_input(directory_input)

    def load_input(self, input_paths: str | Path | list[str | Path]):
        try:
            self.input_handler.load_input(input_paths)
            if len(self.input_handler) == 0:
                self.notify_warning('Keine Versuchsflächen gefunden!')
            else:
                self.input_handler.sort()
        except Exception as err:
            logger.error(err)
            traceback.print_exc()
            self.notify_error('Fehler während des Einlesen der Dateien', err, traceback.format_exc())
            self.input_handler.clear()
        finally:
            self.update_input_status()

    @Slot()
    def create(self):
        if len(self.input_handler) == 0:
            self.notify_warning('Keine Versuchsflächen ausgewählt!')
            return
        output_path = QFileDialog.getSaveFileName(
            parent=self,
            caption='Dateispeicherort',
            filter='Excel-Datei (*.xlsx)'
        )[0]

        # empty path is returned if the dialog is cancelled
        if not output_path:
            return

        if not output_path.endswith('.xlsx'):
            output_path += '.xlsx'

        self.progress_bar.setMinimum(0)
        # last step is formatting and metadata writing
        self.progress_bar.setMaximum(len(self.input_handler) + 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.manage_space()

        try:
            # allow overriding (exit_ok=True) because QFileDialog already asks whether to allow
            for _ in self.input_handler.createAll(Path(output_path), exist_ok=True):
                self.progress_bar.setValue(self.progress_bar.value() + 1)
            self.notify_success('Formular erstellt')
            self.progress_bar.setVisible(False)
            self.manage_space()
        except Exception as err:
            logger.error(err)
            traceback.print_exc()
            self.notify_error('Fehler während des Speichern der Dateien', err, traceback.format_exc())
        finally:
            self.progress_bar.setVisible(False)

    @Slot()
    def notify_success(self, message: str):
        self.notification(message, None, None, icon=QMessageBox.Icon.Information)

    @Slot()
    def notify_warning(self, message: str):
        self.notification(message, None, None, icon=QMessageBox.Icon.Warning)

    @Slot()
    def notify_error(self, message: str, exception: Exception, traceback: str):
        self.notification(text=message,
                          informative_text=f'{type(exception).__name__}: {str(exception)}',
                          detailed_text=traceback,
                          icon=QMessageBox.Icon.Critical
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

    def update_input_status(self):
        trial_site_count = len(self.input_handler)
        if trial_site_count == 0:
            self.status_label.setText('Es sind keine Versuchsflächen ausgewählt.')
            self.status_table.setVisible(False)
        else:
            self.status_label.setText(f'{trial_site_count} Versuchsflächen sind ausgewählt:')

            self.status_table.clear()
            self.status_table.setVisible(True)
            self.status_table.setHorizontalHeaderLabels(('Versuch', 'Parzelle', 'entfernen'))
            self.status_table.setRowCount(trial_site_count)
            for row, trial_site in enumerate(self.input_handler.trial_sites):
                widget0 = QTableWidgetItem(trial_site.metadata['Versuch'])
                widget0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                widget1 = QTableWidgetItem(trial_site.metadata['Parzelle'])
                widget1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.status_table.setItem(row, 0, widget0)
                self.status_table.setItem(row, 1, widget1)
        self.manage_space()

    """
    Shamelessly stolen from https://stackoverflow.com/a/41543029
    """

    def getQTableWidgetSize(self) -> QSize:
        self.status_table.resizeRowsToContents()
        width = self.status_table.verticalHeader().width() + 4  # +4 seems to be needed
        for i in range(self.status_table.columnCount()):
            width += self.status_table.columnWidth(i)  # seems to include gridline (on my machine)
        height = self.status_table.horizontalHeader().height() + 4
        # limit the shown rows to 20
        for i in range(min((self.status_table.rowCount()), 20)):
            height += self.status_table.rowHeight(i)
        return QSize(width, height)

    def manage_space(self) -> None:
        table_widget_size = self.getQTableWidgetSize()
        self.status_table.setMinimumHeight(table_widget_size.height())
        self.status_table.setMaximumHeight(table_widget_size.height())
        # this needs to be done after setting size constraints for the table so these changes are taken into account
        root_size_hint = self.sizeHint()
        self.setMinimumSize(root_size_hint)
        self.setMaximumSize(root_size_hint)