import sys
import os
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QComboBox,
    QWidget, QGridLayout, QMessageBox, QTextEdit, QSizePolicy, QFileDialog, QLineEdit, QVBoxLayout
)
from PyQt6.QtCore import QThreadPool, Qt, QSettings
from PyQt6.QtGui import QIcon, QTextCursor
from utils.Input import HoverButton
from AutomacaoBlume import Blume, AutomationTask

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Estilo da interface gráfica
        self.setStyleSheet("""         
            QLabel {
                font-family: 'Open Sans';
                font-size: 12px;
                color: white;
            }
            QGroupBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 20px;
            }
            QGroupBox:title {
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        # Carregar dados do Excel
        self.data_path = "resources/coleta.xlsx"
        self.df = pd.read_excel(self.data_path)
        self.df = self.df[self.df['STATUS'] != 'COLETADO IA']
        self.df = self.df.sort_values(by='VENCIMENTO', ascending=True)

        # Configurar a janela principal
        self.setWindowTitle("LE - Automação de Coleta")
        self.setWindowIcon(QIcon("resources/logo.ico"))
        self.setGeometry(100, 100, 800, 450)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Inicializar o diretório de salvamento e outras configurações
        self.settings = QSettings("LE - Automacao de Coleta", "Settings")
        self.save_directory = self.settings.value("save_directory", "")

        # Inicializar a interface do usuário
        self.init_ui()

        # Thread pool
        self.threadpool = QThreadPool()

    def init_ui(self):
        # Layout superior
        top_layout = QGridLayout()

        # Diretório de Salvamento
        self.save_dir_field = QLineEdit(self)
        self.save_dir_field.setReadOnly(True)
        self.save_dir_field.setText(self.save_directory)
        top_layout.addWidget(QLabel("Local de Salvamento:"), 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        top_layout.addWidget(self.save_dir_field, 0, 1)
        self.save_dir_button = HoverButton("Selecionar Pasta", self)
        self.save_dir_button.clicked.connect(self.select_save_directory)
        top_layout.addWidget(self.save_dir_button, 0, 2)

        # Seleção de Operadora
        self.operadora_combo = QComboBox(self)
        operadoras = self.df['OPERADORA'].dropna().unique()
        self.operadora_combo.addItems(operadoras)
        top_layout.addWidget(QLabel("Selecionar Operadora:"), 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(self.operadora_combo, 1, 1)

        self.confirm_button = HoverButton("Iniciar automação", self)
        self.confirm_button.clicked.connect(self.start_automation)

        top_layout.addWidget(self.confirm_button, 1, 2)

        self.layout.addLayout(top_layout)

        # Layout dos Logs
        logs_layout = QGridLayout()

        # Área para Log Técnico
        self.log_tecnico_area = QTextEdit(self)
        self.log_tecnico_area.setReadOnly(True)
        self.log_tecnico_area.setPlaceholderText("Log técnico")
        self.log_tecnico_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                background-color: #262525;
                padding: 5px;
            }
        """)
        logs_layout.addWidget(self.log_tecnico_area, 0, 0, 2, 2)

        # Área para Log Faturas Coletadas
        self.faturas_coletadas_area = QTextEdit(self)
        self.faturas_coletadas_area.setReadOnly(True)
        self.faturas_coletadas_area.setPlaceholderText("Log faturas coletadas")
        self.faturas_coletadas_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                background-color: #262525;
                padding: 5px;
            }
        """)
        logs_layout.addWidget(self.faturas_coletadas_area, 0, 2, 2, 2)

        logs_layout.setVerticalSpacing(10)
        logs_layout.setHorizontalSpacing(10)

        logs_layout.setColumnStretch(0, 2)
        logs_layout.setColumnStretch(1, 3)
        logs_layout.setColumnStretch(2, 2)
        logs_layout.setColumnStretch(3, 3)

        self.layout.addLayout(logs_layout)

        # Configurações adicionais de layout
        top_layout.setColumnStretch(0, 1)
        top_layout.setColumnStretch(1, 4)
        top_layout.setColumnStretch(2, 1)

        logs_layout.setRowStretch(0, 2)
        logs_layout.setRowStretch(1, 4)

        # Configurações de tamanho
        self.save_dir_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.operadora_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.confirm_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.save_dir_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.log_tecnico_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.faturas_coletadas_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def select_save_directory(self):
        # Abrir o diálogo para selecionar diretório de salvamento
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Diretório de Salvamento")
        if dir_path:
            self.save_directory = dir_path
            self.settings.setValue("save_directory", dir_path)
            QMessageBox.information(self, "Diretório Selecionado", f"Diretório de salvamento selecionado: {dir_path}")
        else:
            self.save_directory = ""

    def log_message(self, message, area="tecnico"):
        # Exibir mensagem no log específico (técnico ou faturas)
        if area == "tecnico":
            self.log_tecnico_area.append(message)
            cursor = self.log_tecnico_area.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_tecnico_area.setTextCursor(cursor)
        elif area == "faturas":
            self.faturas_coletadas_area.append(message)
            cursor = self.faturas_coletadas_area.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.faturas_coletadas_area.setTextCursor(cursor)

    def start_automation(self):
        # Início do processo de automação
        selected_operadora = self.operadora_combo.currentText()

        if not self.save_directory:
            QMessageBox.warning(self, "Erro", "Selecione um diretório de salvamento primeiro.")
            return

        if not selected_operadora:
            QMessageBox.warning(self, "Erro", "Selecione uma operadora.")
            return

        user_data = self.df[self.df['OPERADORA'] == selected_operadora]
        if user_data.empty:
            QMessageBox.warning(self, "Erro", f"Nenhum dado encontrado para a operadora {selected_operadora}.")
            return

        if selected_operadora.upper() == "BLUME":
            automator = Blume(self, self.df)
        else:
            QMessageBox.warning(self, "Erro", f"Automação para a operadora {selected_operadora} não está implementada.")
            return

        task = AutomationTask(automator, user_data, self.log_message)
        self.threadpool.start(task)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())
