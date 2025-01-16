import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QLabel, QComboBox,
    QWidget, QGridLayout, QMessageBox, QTextEdit, QSizePolicy, QFileDialog, QLineEdit, QVBoxLayout, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import QThreadPool, Qt, QSettings, QSize
from PyQt6.QtGui import QIcon, QTextCursor, QPixmap
from openpyxl import load_workbook

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from autoBlume import Blume, AutomationTask
from templates.GerenJanela import ResizableWindow
from templates.GerenEstilos import estilo_sheet, estilo_label, estilo_log, campo_qline, estilo_combo_box, estilo_hover


class GuiAutoBlume(QWidget):
    """Interface gráfica para a funcionalidade 'Automação coleta'."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.workbook = None
        self.sheet = None
        self.data_path = ""
        self.save_directory = ""
        self.threadpool = QThreadPool()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

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
        self.save_dir_field.setStyleSheet(campo_qline())
        top_layout.addWidget(self.save_dir_field, 0, 1)

        self.save_dir_button = QPushButton("Selecionar Pasta", self)
        estilo_hover(self.save_dir_button)
        self.save_dir_button.clicked.connect(self.select_save_directory)
        top_layout.addWidget(self.save_dir_button, 0, 2)

        # Seleção de Planilha
        self.planilha_field = QLineEdit(self)
        self.planilha_field.setReadOnly(True)
        self.planilha_field.setText(self.data_path)
        self.planilha_field.setStyleSheet(campo_qline())
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

        self.layout.addLayout(logs_layout)

    def select_data_file(self):
        last_dir = QSettings(self.parent.settings_path, QSettings.Format.IniFormat).value("last_open_dir", "")
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

            self.parent.save_settings()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar a planilha: {e}")

    def select_save_directory(self):
        last_save_dir = QSettings(self.parent.settings_path, QSettings.Format.IniFormat).value("last_save_dir", "")
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Diretório de Salvamento", last_save_dir)

        if dir_path:
            self.save_directory = dir_path
            self.save_dir_field.setText(dir_path)
            self.parent.save_settings()
        else:
            self.save_directory = ""

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
            task = AutomationTask(automator, self.get_user_data(selected_operadora), self.log_message)
            self.threadpool.start(task)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar a tarefa de automação: {e}")

    def get_user_data(self, selected_operadora):
        """Filtra os dados da operadora selecionada."""
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
        return user_data

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


class MainApp(ResizableWindow):
    def __init__(self):
        super().__init__()

        # Configuração da interface gráfica
        self.setStyleSheet(estilo_sheet())

        # Remove a barra de título padrão do sistema operacional
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Fundo transparente

        # Configurações persistentes
        self.settings_path = "config.ini"
        self.save_directory = ""
        self.data_path = ""

        # Configurar a janela principal
        self.setWindowTitle("LE Helper")
        self.setGeometry(100, 100, 900, 550)

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
        layout_titulo.addWidget(icone_titulo)

        # ComboBox para selecionar funcionalidades
        self.funcionalidades_combo = QComboBox(self.barra_titulo)
        self.funcionalidades_combo.addItem("Automação coleta")
        self.funcionalidades_combo.setStyleSheet(estilo_combo_box())
        self.funcionalidades_combo.currentTextChanged.connect(self.mudar_funcionalidade)
        layout_titulo.addWidget(self.funcionalidades_combo)

        # Espaçador para alinhar os botões à direita
        layout_titulo.addStretch()

        # Botão de minimizar
        self.botao_minimizar = QPushButton(self.barra_titulo)
        self.botao_minimizar.setObjectName("botao_minimizar")
        self.botao_minimizar.setIcon(QIcon("frontend/static/icons/minimize.png"))
        self.botao_minimizar.setFixedSize(QSize(20, 20))
        self.botao_minimizar.clicked.connect(self.showMinimized)
        layout_titulo.addWidget(self.botao_minimizar)

        # Botão de fechar
        self.botao_fechar = QPushButton(self.barra_titulo)
        self.botao_fechar.setObjectName("botao_fechar")
        self.botao_fechar.setIcon(QIcon("frontend/static/icons/exit.png"))
        self.botao_fechar.setFixedSize(QSize(20, 20))
        self.botao_fechar.clicked.connect(self.close)
        layout_titulo.addWidget(self.botao_fechar)

        # Adiciona a barra de título personalizada ao layout principal
        self.layout.addWidget(self.barra_titulo)

        # Widget central e layout principal
        self.central_content = QWidget(self.central_widget)
        self.layout.addWidget(self.central_content)
        self.content_layout = QVBoxLayout(self.central_content)

        # Inicializa a funcionalidade padrão
        self.gui_auto_blume = GuiAutoBlume(self)
        self.content_layout.addWidget(self.gui_auto_blume)

    def mudar_funcionalidade(self, funcionalidade):
        """Alterna entre as funcionalidades disponíveis."""
        if funcionalidade == "Automação coleta":
            self.content_layout.addWidget(self.gui_auto_blume)
        else:
            # Adicione outras funcionalidades aqui
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())