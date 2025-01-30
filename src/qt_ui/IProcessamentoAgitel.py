import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit,
    QFileDialog, QProgressBar, QTextEdit, QCheckBox,
    QLabel, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QSettings, Qt
from utils.GerenEstilos import (
    estilo_label_light, estilo_label_dark,
    campo_qline_light, campo_qline_dark,
    estilo_check_box_light, estilo_check_box_dark,
    estilo_log_light, estilo_log_dark,
    estilo_progress_bar_light, estilo_progress_bar_dark,
    estilo_hover
)

class PainelProcessamentoAgitel(QWidget):
    processStarted = pyqtSignal()
    processFinished = pyqtSignal(str)
    progressUpdated = pyqtSignal(int)
    errorOccurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.init_ui()
        self._connect_signals()

    def init_ui(self):
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

        self.btn_select_file.clicked.connect(self._emit_select_file)
        self.btn_process.clicked.connect(self._emit_process_file)

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

    def _connect_signals(self):
        self.progressUpdated.connect(self.update_progress)
        self.processFinished.connect(self.on_process_finished)
        self.errorOccurred.connect(self.show_error)

    def _emit_select_file(self):
        settings = QSettings("LivreEscolha", "LE_Helper")
        last_dir = settings.value("last_open_dir", "")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo Excel", last_dir, "Excel Files (*.xlsx)"
        )
        if file_path:
            self.text_file.setText(file_path)
            settings.setValue("last_open_dir", os.path.dirname(file_path))
            self.append_log(f"📂 Arquivo selecionado: {os.path.basename(file_path)}")

    def _emit_process_file(self):
        if not self.text_file.text():
            self.append_log("⚠️ Selecione um arquivo antes de processar!")
            return
        self.append_log("⏳ Iniciando processamento...")
        self.processStarted.emit()

    @pyqtSlot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.append_log("✅ Processamento concluído, salvando arquivo!")

    @pyqtSlot(str)
    def on_process_finished(self, message):
        self.btn_process.setEnabled(True)
        self.append_log("──────────────────────────────────────────────────")
        self.append_log(f"🎉 {message}")

    @pyqtSlot(str)
    def append_log(self, message):
        color = "#e0e0e0" if self.is_dark_mode else "#333333"
        self.text_results.append(f'<span style="color: {color}">{message}</span>')
        self.scroll_to_bottom()

    @pyqtSlot(str)
    def show_error(self, message):
        self.append_log(f"⛔ ERRO: {message}")
        self.append_log("🛑 Processamento interrompido!")
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        self.text_results.verticalScrollBar().setValue(
            self.text_results.verticalScrollBar().maximum()
        )

    def get_file_path(self):
        return self.text_file.text()

    def get_equalize_option(self):
        return self.checkbox_equalize.isChecked()

    def set_processing_state(self, processing):
        self.btn_process.setEnabled(not processing)
        self.btn_select_file.setEnabled(not processing)
        status = "Processando..." if processing else "Pronto"
        self.append_log(f"📢 Status: {status}")