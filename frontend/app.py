import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QLabel, QComboBox,
    QWidget, QGridLayout, QMessageBox, QTextEdit, QSizePolicy, QFileDialog, QLineEdit, QVBoxLayout, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import QThreadPool, Qt, QSettings, QSize
from PyQt6.QtGui import QIcon, QTextCursor, QPixmap
from templates.estilos import estilo_sheet, estilo_label, estilo_log, qLine, estilo_combo_box, estilo_hover
from openpyxl import load_workbook

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from autoBlume import Blume, AutomationTask
from templates.resize import ResizableWindow


class MainApp(ResizableWindow):
    def __init__(self):
        super().__init__()

        # Configuração da interface gráfica
        self.setStyleSheet(estilo_sheet())

        # Remove a barra de título padrão do sistema operacional
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Fundo transparente

        # Configurações persistentes
        self.settings_path = "config.json"
        self.load_settings()

        # Configurar a janela principal
        self.setWindowTitle("LE Helper")  # Título da janela
        self.setGeometry(100, 100, 900, 550)  # Tamanho e posição da janela

        # Cria um widget central com bordas arredondadas
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setStyleSheet("""
            QWidget#central_widget {
                background-color: #f4f4f4;
                border-radius: 12px;
                border: 1px solid #cccccc;
            }
        """)
        self.setCentralWidget(self.central_widget)

        # Layout principal
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Cria uma barra de título personalizada
        self.barra_titulo = QWidget(self.central_widget)
        self.barra_titulo.setObjectName("barra_titulo")
        self.barra_titulo.setFixedHeight(30)

        layout_titulo = QHBoxLayout(self.barra_titulo)
        layout_titulo.setContentsMargins(5, 0, 5, 0)
        layout_titulo.setSpacing(5)

        titulo_widget = QWidget()
        titulo_layout = QHBoxLayout(titulo_widget)
        titulo_layout.setContentsMargins(0, 0, 0, 0)
        titulo_layout.setSpacing(0)

        # Ícone do título
        caminho_base = os.path.join(os.path.dirname(__file__), "..", "frontend", "static", "images")
        icone_titulo = QLabel()
        caminho_icone = os.path.join(caminho_base, "logo.png")
        if os.path.exists(caminho_icone):
            icone_titulo.setPixmap(QPixmap(caminho_icone).scaled(
                24, 24, 
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            print(f"Arquivo de ícone não encontrado: {caminho_icone}")

        titulo_layout.addWidget(icone_titulo)

        # Adiciona o widget do título ao layout da barra de título
        layout_titulo.addWidget(titulo_widget)

        # Espaçador para alinhar os botões à direita
        layout_titulo.addStretch()

        # Botão de minimizar
        self.botao_minimizar = QPushButton()
        self.botao_minimizar.setObjectName("botao_minimizar")
        self.botao_minimizar.setIcon(QIcon("frontend/static/icons/minimize.png"))  # Ícone de minimizar
        self.botao_minimizar.setFixedSize(QSize(20, 20))  # Tamanho fixo
        self.botao_minimizar.clicked.connect(self.showMinimized)  # Conecta ao método de minimizar
        layout_titulo.addWidget(self.botao_minimizar)

        # Botão de fechar
        self.botao_fechar = QPushButton()
        self.botao_fechar.setObjectName("botao_fechar")
        self.botao_fechar.setIcon(QIcon("frontend/static/icons/exit.png"))  # Ícone de fechar
        self.botao_fechar.setFixedSize(QSize(20, 20))  # Tamanho fixo
        self.botao_fechar.clicked.connect(self.close)  # Conecta ao método de fechar
        layout_titulo.addWidget(self.botao_fechar)

        # Adiciona a barra de título personalizada ao layout principal
        self.layout.addWidget(self.barra_titulo)

        # Widget central e layout principal
        self.central_content = QWidget()
        self.layout.addWidget(self.central_content)
        self.content_layout = QVBoxLayout(self.central_content)

        self.workbook = None  # Workbook do Excel
        self.sheet = None  # Planilha ativa
        self.data_path = ""  # Caminho do arquivo Excel

        self.load_settings()  # Carrega as configurações persistentes
        self.init_ui()  # Inicializa a interface do usuário
        self.threadpool = QThreadPool()  # Pool de threads para execução de tarefas

        # Carrega a planilha se já estiver definida
        if self.data_path:
            self.load_data_file(self.data_path)
        else:
            self.select_data_file()

    def load_settings(self):
        settings = QSettings(self.settings_path, QSettings.Format.IniFormat)
        self.save_directory = settings.value("save_directory", "")
        self.data_path = settings.value("data_path", "")

    def save_settings(self):
        settings = QSettings(self.settings_path, QSettings.Format.IniFormat)
        settings.setValue("save_directory", self.save_directory)
        settings.setValue("data_path", self.data_path)
        settings.setValue("last_open_dir", os.path.dirname(self.data_path))
        settings.sync()

    def init_ui(self):
        top_layout = QGridLayout()

        # Aplicar estilo ao QLabel
        label_salvamento = QLabel("Local de Salvamento:", self)
        label_salvamento.setStyleSheet(estilo_label())
        label_planilha = QLabel("Planilha de dados:", self)
        label_planilha.setStyleSheet(estilo_label())
        label_operadora = QLabel("Selecionar Operadora:", self)
        label_operadora.setStyleSheet(estilo_label())

        top_layout.addWidget(label_salvamento, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        top_layout.addWidget(label_planilha, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        top_layout.addWidget(label_operadora, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        # Diretório de Salvamento
        self.save_dir_field = QLineEdit(self)
        self.save_dir_field.setReadOnly(True)
        self.save_dir_field.setText(self.save_directory)
        self.save_dir_field.setStyleSheet(qLine())
        top_layout.addWidget(self.save_dir_field, 0, 1)

        self.save_dir_button = QPushButton("Selecionar Pasta", self)
        estilo_hover(self.save_dir_button)
        self.save_dir_button.clicked.connect(self.select_save_directory)
        top_layout.addWidget(self.save_dir_button, 0, 2)

        # Seleção de Planilha
        self.planilha_field = QLineEdit(self)
        self.planilha_field.setReadOnly(True)
        self.planilha_field.setText(self.data_path)
        self.planilha_field.setStyleSheet(qLine())
        top_layout.addWidget(self.planilha_field, 1, 1)

        self.planilha_button = QPushButton("Selecionar Planilha", self)
        estilo_hover(self.planilha_button)
        self.planilha_button.clicked.connect(self.select_data_file)
        top_layout.addWidget(self.planilha_button, 1, 2)

        # Seleção de Operadora
        self.operadora_combo = QComboBox(self)
        self.operadora_combo.addItem("Selecione uma planilha primeiro")
        self.operadora_combo.setStyleSheet(estilo_combo_box())
        top_layout.addWidget(self.operadora_combo, 2, 1)

        self.confirm_button = QPushButton("Iniciar automação", self)
        estilo_hover(self.confirm_button)
        self.confirm_button.clicked.connect(self.start_automation)
        top_layout.addWidget(self.confirm_button, 2, 2)

        self.layout.addLayout(top_layout)

        # Layout dos Logs
        logs_layout = QGridLayout()

        # Aplicar estilo ao QTextEdit
        self.log_tecnico_area = QTextEdit(self)
        self.log_tecnico_area.setReadOnly(True)
        self.log_tecnico_area.setPlaceholderText("Log técnico")
        self.log_tecnico_area.setStyleSheet(estilo_log())
        logs_layout.addWidget(self.log_tecnico_area, 0, 0, 2, 2)

        self.faturas_coletadas_area = QTextEdit(self)
        self.faturas_coletadas_area.setReadOnly(True)
        self.faturas_coletadas_area.setPlaceholderText("Log faturas coletadas")
        self.faturas_coletadas_area.setStyleSheet(estilo_log())
        logs_layout.addWidget(self.faturas_coletadas_area, 0, 2, 2, 2)

        # Melhorar layout de logs
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
        self.planilha_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.operadora_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.confirm_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.save_dir_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.planilha_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.log_tecnico_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.faturas_coletadas_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def select_data_file(self):
        last_dir = QSettings(self.settings_path, QSettings.Format.IniFormat).value("last_open_dir", "")
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Planilha de Dados", last_dir, "Arquivos Excel (*.xlsx *.xlsm)")

        if file_path:
            self.load_data_file(file_path)

    def load_data_file(self, file_path):
        """Carrega a planilha de dados e atualiza a interface."""
        try:
            self.workbook = load_workbook(file_path)
            self.sheet = self.workbook.active
            self.data_path = file_path
            self.planilha_field.setText(file_path)

            # Atualiza o combo de operadoras
            self.operadora_combo.clear()
            operadoras = set()
            for row in self.sheet.iter_rows(min_row=2, values_only=True):
                if row[3]:  # Coluna 3: OPERADORA
                    operadoras.add(row[3])
            self.operadora_combo.addItems(operadoras)

            self.save_settings()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar a planilha: {e}")

    def select_save_directory(self):
        last_save_dir = QSettings(self.settings_path, QSettings.Format.IniFormat).value("last_save_dir", "")
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Diretório de Salvamento", last_save_dir)

        if dir_path:
            self.save_directory = dir_path
            self.save_dir_field.setText(dir_path)

            settings = QSettings(self.settings_path, QSettings.Format.IniFormat)
            settings.setValue("save_directory", dir_path)
            settings.setValue("last_save_dir", dir_path)

            self.save_settings()
        else:
            self.save_directory = ""

    def log_message(self, message, area="tecnico"):
        """Exibe mensagens nos logs adequados."""
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
        """Inicia o processo de automação."""
        selected_operadora = self.operadora_combo.currentText()

        if not self.save_directory:
            QMessageBox.warning(self, "Erro", "Selecione um diretório de salvamento primeiro.")
            return

        if not selected_operadora:
            QMessageBox.warning(self, "Erro", "Selecione uma operadora.")
            return

        if not self.data_path:
            QMessageBox.warning(self, "Erro", "Selecione uma planilha de dados primeiro.")
            return

        if not self.workbook:
            QMessageBox.warning(self, "Erro", "A planilha de dados ainda não foi carregada.")
            return

        # Filtra os dados da operadora selecionada
        user_data = []
        for row in self.sheet.iter_rows(min_row=2, values_only=True):
            if row[3] == selected_operadora and row[11] != 'COLETADO IA':  # Coluna 3: OPERADORA, Coluna 11: STATUS
                user_data.append({
                    "FORNECEDOR": row[0],
                    "REFERÊNCIA": row[1],
                    "CLIENTE": row[2],
                    "OPERADORA": row[3],
                    "IDENTIFICAÇÃO": row[4],
                    "CÓDIGO": row[5],
                    "PA": row[6],
                    "INDENTIFICAÇÃO INTERNA": row[7],
                    "LOGIN": row[8],
                    "SENHA": row[9],
                    "VENCIMENTO": row[10],
                    "STATUS": row[11],
                    "NOMENCLATURA": row[12]
                })

        if not user_data:
            QMessageBox.warning(self, "Erro", f"Nenhum dado encontrado para a operadora {selected_operadora}.")
            return

        if selected_operadora.upper() == "BLUME":
            try:
                automator = Blume(self, self.data_path)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao criar o automator Blume: {e}")
                return
        else:
            QMessageBox.warning(self, "Erro", f"Automação para a operadora {selected_operadora} não está implementada.")
            return

        try:
            task = AutomationTask(automator, user_data, self.log_message)
            self.threadpool.start(task)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar a tarefa de automação: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())