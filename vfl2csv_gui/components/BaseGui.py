import logging
import traceback
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QTableWidget,
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QFileDialog,
    QTableWidgetItem,
    QProgressBar,
    QSizePolicy,
    QCheckBox,
)

from vfl2csv_gui.components.QHLine import QHLine
from vfl2csv_gui.interfaces.AbstractInputHandler import AbstractInputHandler
from vfl2csv_gui.interfaces.ConversionGuiConfig import ConversionGuiConfig

logger = logging.getLogger(__name__)


class BaseGui(QWidget):
    def __init__(
            self, config: ConversionGuiConfig, input_handler: AbstractInputHandler
    ):
        super().__init__()
        self.text_map = config.text_map
        self.output_is_file = config.output_is_file
        self.output_file_format = config.output_file_extension
        self.input_handler = input_handler

        layout = QVBoxLayout()

        self.setWindowTitle(self.text_map["window-title"])
        title = QLabel(self.text_map["content-title"])
        title_font = title.font()
        title_font.setPointSize(24)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # title margins like to expand when resizing the window vertically. Disable this
        title.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        )

        caption = QLabel(self.text_map["content-caption"])
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        )
        caption.setWordWrap(True)

        single_file_input = QPushButton(self.text_map["input-files"])
        single_file_input.clicked.connect(self.single_file_input)
        directory_input = QPushButton(self.text_map["input-directory"])
        directory_input.clicked.connect(self.directory_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(single_file_input, stretch=3)
        button_layout.addWidget(
            QLabel(text="oder", alignment=Qt.AlignmentFlag.AlignCenter), stretch=1
        )
        button_layout.addWidget(directory_input, stretch=3)

        self.status_label = QLabel(
            text=self.text_map["no-files-selected"],
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        self.status_table = QTableWidget(0, len(self.text_map["list-headers"]))
        self.status_table.setVisible(False)
        self.status_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setting_checkboxes: dict[str, QCheckBox] = {}
        for key in config.boolean_options:
            self.setting_checkboxes[key] = QCheckBox(self.text_map[key])
        self.run_button = QPushButton(self.text_map["convert"])
        self.run_button.clicked.connect(self.create)
        self.run_button.setMinimumHeight(50)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        layout.addWidget(title)
        layout.addWidget(caption)
        layout.addLayout(button_layout)
        layout.addWidget(QHLine())
        layout.addWidget(self.status_label)
        layout.addWidget(self.status_table)
        layout.addWidget(QHLine())
        for checkbox in self.setting_checkboxes.values():
            layout.addWidget(checkbox)
        layout.addWidget(self.run_button)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.update_input_status()

    @Slot()
    def single_file_input(self) -> None:
        files_input: tuple[list[Path], str] = QFileDialog.getOpenFileNames(
            parent=self,
            caption=self.text_map["filedialog-input-single-file"],
            filter=self.text_map["filedialog-input-single-file-filter"],
        )
        # the first value of the tuple is a list of selected file names. This list is empty, if the dialog is cancelled
        if len(files_input[0]) == 0:
            return

        self.load_input(files_input[0])

    @Slot()
    def directory_input(self) -> None:
        directory_input: str = QFileDialog.getExistingDirectory(
            parent=self,
            caption=self.text_map["filedialog-input-dictionary"],
            options=QFileDialog.ShowDirsOnly,
        )
        # only the selected path is returned, nothing else
        if directory_input == "":
            return

        self.load_input(directory_input)

    def load_input(self, input_paths: str | Path | list[str | Path]) -> None:
        self.input_handler.clear()
        try:
            self.input_handler.load_input(input_paths)
        except Exception as exc:
            self.handle_exception(exc)

        if len(self.input_handler) == 0:
            self.notify_warning(self.text_map["input-no-files-found"])
        else:
            self.input_handler.sort()
        self.update_input_status()

    @Slot()
    def create(self) -> None:
        if len(self.input_handler) == 0:
            self.notify_warning(self.text_map["error-no-files-selected"])
            return
        output_path: str
        if self.output_is_file:
            output_path = QFileDialog.getSaveFileName(
                parent=self,
                caption=self.text_map["filedialog-output"],
                filter=self.text_map["filedialog-output-filter"],
            )[0]
            if not output_path.endswith(f".{self.output_file_format}"):
                output_path += f".{self.output_file_format}"
        else:
            output_path = QFileDialog.getExistingDirectory(
                parent=self,
                caption=self.text_map["filedialog-output"],
                options=QFileDialog.ShowDirsOnly,
            )
        # empty path is returned if the dialog is cancelled
        if output_path == "":
            return

        if self.output_is_file and not output_path.endswith(
                f".{self.output_file_format}"
        ):
            output_path += f".{self.output_file_format}"

        setting_values = {
            key: checkbox.isChecked()
            for key, checkbox in self.setting_checkboxes.items()
        }

        steps, signals = self.input_handler.convert(Path(output_path), setting_values)
        self.setup_progress_bar(steps)
        signals.progress.connect(self.increment_progress_bar)
        signals.finished.connect(self.finish_conversion)
        signals.error.connect(
            lambda exception: self.finish_conversion(success=False, exception=exception)
        )

    def setup_progress_bar(self, steps: int):
        self.progress_bar.setMinimum(0)
        # one step for each trial site
        self.progress_bar.setMaximum(steps)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.manage_space()
        self.run_button.setDisabled(True)

    @Slot(str)
    def increment_progress_bar(self):
        self.progress_bar.setValue(self.progress_bar.value() + 1)

    @Slot()
    def finish_conversion(self, success: bool = True, exception: Exception = None):
        if success:
            self.notify_success(self.text_map["done"])
        elif exception:
            self.handle_exception(exception)
        self.progress_bar.setVisible(False)
        self.manage_space()
        self.run_button.setDisabled(False)

    def notify_success(self, message: str) -> None:
        self.notification(message, None, None, icon=QMessageBox.Icon.Information)

    def notify_warning(self, message: str) -> None:
        self.notification(message, None, None, icon=QMessageBox.Icon.Warning)

    def notify_error(self, message: str, exception: Exception) -> None:
        informative_text = f"{type(exception).__name__}: {str(exception)}"
        if exception.__cause__:
            informative_text += f". Caused by: {str(exception.__cause__)}"
        if isinstance(exception, ExceptionGroup):
            for i, nested_exception in enumerate(exception.exceptions):
                informative_text += f"\n{i + 1}. {type(nested_exception).__name__}: {str(nested_exception)}"
                if exception.__cause__:
                    informative_text += f". Caused by: {str(exception.__cause__)}"

        self.notification(
            text=message,
            informative_text=informative_text,
            detailed_text="\n".join(traceback.format_tb(exception.__traceback__)),
            icon=QMessageBox.Icon.Critical,
        )

    @Slot()
    def handle_exception(self, exception: Exception) -> None:
        self.notify_error(self.text_map["conversion-error-title"], exception)

    def notification(
            self,
            text: str,
            informative_text: Optional[str],
            detailed_text: Optional[str],
            icon: QMessageBox.Icon,
    ) -> None:
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon or QMessageBox.Icon.NoIcon)
        msg_box.setText(text)
        if informative_text is not None:
            msg_box.setInformativeText(informative_text)
        if detailed_text is not None:
            msg_box.setDetailedText(detailed_text)
        msg_box.exec()

    def update_input_status(self) -> None:
        trial_site_count = len(self.input_handler)
        if trial_site_count == 0:
            self.status_label.setText(self.text_map["no-files-selected"])
            self.status_table.setVisible(False)
        else:
            self.status_label.setText(
                self.text_map.get_replace("n-files-selected", trial_site_count)
            )

            self.status_table.clear()
            self.status_table.setVisible(True)
            self.status_table.setHorizontalHeaderLabels(self.text_map["list-headers"])
            self.status_table.setRowCount(trial_site_count)
            for row, representation in enumerate(
                    self.input_handler.table_representation()
            ):
                for col, value in enumerate(representation):
                    widget = QTableWidgetItem(value)
                    widget.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.status_table.setItem(row, col, widget)
        self.manage_space()

    def get_qtable_widget_size(self) -> QSize:
        """
        Shamelessly stolen from https://stackoverflow.com/a/41543029
        """
        self.status_table.resizeRowsToContents()
        width = self.status_table.verticalHeader().width() + 4
        # +4 seems to be needed
        for i in range(self.status_table.columnCount()):
            width += self.status_table.columnWidth(i)
        height = self.status_table.horizontalHeader().height() + 4
        # limit the number of shown rows to 10
        for i in range(min((self.status_table.rowCount()), 10)):
            height += self.status_table.rowHeight(i)
        return QSize(width, height)

    def manage_space(self) -> None:
        self.status_table.setMinimumHeight(self.get_qtable_widget_size().height())
