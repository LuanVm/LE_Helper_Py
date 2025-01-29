# Interface de Usuário - IProcessamentoAgitel.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit,
    QFileDialog, QProgressBar, QTextEdit, QCheckBox,
    QMessageBox, QLabel, QHBoxLayout, QApplication
)
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QCloseEvent
from utils.GerenEstilos import (
    estilo_label_light, estilo_label_dark,
    campo_qline_light, campo_qline_dark,
    estilo_check_box_light, estilo_check_box_dark,
    estilo_log_light, estilo_log_dark,
    estilo_progress_bar_light, estilo_progress_bar_dark,
    estilo_hover
)

class PainelProcessamentoAgitel(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.is_dark_mode = False
        self._init_ui()
        self._connect_signals()
        self._load_settings()

    def _init_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(15, 15, 15, 15)
        self.layout().setSpacing(10)

        self._create_file_controls()
        self._create_progress_bar()
        self._create_results_area()

    def _create_file_controls(self):
        grid = QGridLayout()
        grid.setVerticalSpacing(10)
        grid.setHorizontalSpacing(15)
        grid.setColumnStretch(1, 1)

        self.label_file = QLabel("Arquivo XLSX (Planilha da Agitel):")
        self.text_file = QLineEdit()
        self.text_file.setReadOnly(True)

        self.btn_select_file = QPushButton("Selecionar Arquivo")
        self.btn_select_file.setFixedSize(160, 32)
        self.btn_process = QPushButton("Processar")
        self.btn_process.setFixedSize(160, 32)
        self.checkbox_equalize = QCheckBox("Equalizar 'Região'")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_select_file)
        button_layout.addWidget(self.btn_process)
        button_layout.setSpacing(10)

        grid.addWidget(self.label_file, 0, 0)
        grid.addWidget(self.text_file, 0, 1)
        grid.addLayout(button_layout, 0, 2)
        grid.addWidget(self.checkbox_equalize, 0, 3, Qt.AlignmentFlag.AlignLeft)

        self.layout().addLayout(grid)

    def _create_progress_bar(self):
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.layout().addWidget(self.progress_bar)

    def _create_results_area(self):
        self.text_results = QTextEdit()
        self.text_results.setReadOnly(True)
        self.text_results.setPlaceholderText("Resultados do processamento...")
        self.layout().addWidget(self.text_results)

    def _connect_signals(self):
        self.btn_select_file.clicked.connect(self._select_file)
        self.btn_process.clicked.connect(self._process_file)
        self.controller.progress_updated.connect(self._update_progress)
        self.controller.process_finished.connect(self._on_process_finished)
        self.controller.error_occurred.connect(self._show_error)
        self.controller.log_updated.connect(self._append_log)

    def apply_styles(self, is_dark_mode):
        self.is_dark_mode = is_dark_mode
        styles = {
            'label': estilo_label_dark() if is_dark_mode else estilo_label_light(),
            'line': campo_qline_dark() if is_dark_mode else campo_qline_light(),
            'check': estilo_check_box_dark() if is_dark_mode else estilo_check_box_light(),
            'log': estilo_log_dark() if is_dark_mode else estilo_log_light(),
            'progress': estilo_progress_bar_dark() if is_dark_mode else estilo_progress_bar_light()
        }

        self.label_file.setStyleSheet(styles['label'])
        self.text_file.setStyleSheet(styles['line'])
        self.checkbox_equalize.setStyleSheet(styles['check'])
        self.text_results.setStyleSheet(styles['log'])
        self.progress_bar.setStyleSheet(styles['progress'])

        for btn in [self.btn_select_file, self.btn_process]:
            estilo_hover(btn, is_dark_mode)

    def _select_file(self):
        settings = QSettings("LivreEscolha", "LE_Helper")
        last_dir = settings.value("last_open_dir", "")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo Excel", last_dir, "Excel Files (*.xlsx)"
        )
        if file_path:
            self.text_file.setText(file_path)
            settings.setValue("last_open_dir", os.path.dirname(file_path))

    def _process_file(self):
        file_path = self.text_file.text()
        if self._validate_file(file_path):
            self.progress_bar.reset()
            self.btn_process.setEnabled(False)
            self.controller.processar(
                file_path, 
                self.checkbox_equalize.isChecked()
            )

    def _validate_file(self, file_path):
        if not file_path:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo Excel.")
            return False
        if not os.path.isfile(file_path):
            QMessageBox.warning(self, "Aviso", "Arquivo inválido.")
            return False
        return True

    def _update_progress(self, value):
        self.progress_bar.setValue(value)

    def _on_process_finished(self, message):
        self.btn_process.setEnabled(True)
        self._append_log(message)

    def _append_log(self, message):
        color = "#e0e0e0" if self.is_dark_mode else "#333333"
        self.text_results.append(f'<span style="color: {color}">{message}</span>')
        QApplication.processEvents()

    def _show_error(self, message):
        QMessageBox.critical(self, "Erro", message)
        self._append_log("Processamento interrompido devido a erro crítico")

    def _load_settings(self):
        """Carrega configurações persistentes"""
        settings = QSettings("LivreEscolha", "LE_Helper")
        # Verifica se existe um valor antes de restaurar
        geometry = settings.value("windowGeometry")
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event: QCloseEvent):
        settings = QSettings("LivreEscolha", "LE_Helper")
        # Verifica se a geometria é válida antes de salvar
        if not self.saveGeometry().isEmpty():
            settings.setValue("windowGeometry", self.saveGeometry())
        super().closeEvent(event)