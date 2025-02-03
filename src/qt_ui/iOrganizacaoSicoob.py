import os
import configparser
from pathlib import Path
from collections import defaultdict

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QTextEdit, QLineEdit, QPushButton,
    QGridLayout, QVBoxLayout, QHBoxLayout, QFileDialog,
    QScrollArea, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtGui import QFont, QTextCursor, QIcon

from utils.sheetStyles import (
    estilo_label_light, estilo_label_dark,
    campo_qline_light, campo_qline_dark,
    estilo_log_light, estilo_log_dark,
    estilo_hover
)
from services.OrganizacaoSicoob import OrganizadorSicoobThread

# Editor para o mapeamento de agências (CNPJ -> Agência)
class EditorAgencias(QDialog):
    def __init__(self, agencias, parent=None):
        super().__init__(parent)
        self.agencias = agencias
        self.setWindowTitle("Editor de Agências")
        self.setFixedSize(400, 300)
        caminho_base = Path(__file__).resolve().parent.parent / "resources" / "icons"
        caminho_icone = caminho_base / "logo.ico"
        if caminho_icone.exists():
            self.setWindowIcon(QIcon(str(caminho_icone)))
        
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(2)
        self.tabela.setHorizontalHeaderLabels(["CNPJ", "Agência"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.carregar_dados()
        
        btn_adicionar = QPushButton("Adicionar")
        btn_remover = QPushButton("Remover")
        btn_salvar = QPushButton("Salvar")
        
        btn_adicionar.clicked.connect(self.adicionar_linha)
        btn_remover.clicked.connect(self.remover_linha)
        btn_salvar.clicked.connect(self.salvar)
        
        layout_botoes = QHBoxLayout()
        layout_botoes.addWidget(btn_adicionar)
        layout_botoes.addWidget(btn_remover)
        layout_botoes.addWidget(btn_salvar)
        
        layout_principal = QVBoxLayout()
        layout_principal.addWidget(self.tabela)
        layout_principal.addLayout(layout_botoes)
        
        self.setLayout(layout_principal)

    def carregar_dados(self):
        self.tabela.setRowCount(len(self.agencias))
        for i, (cnpj, agencia) in enumerate(self.agencias.items()):
            self.tabela.setItem(i, 0, QTableWidgetItem(cnpj))
            self.tabela.setItem(i, 1, QTableWidgetItem(agencia))

    def adicionar_linha(self):
        row = self.tabela.rowCount()
        self.tabela.insertRow(row)
        self.tabela.setItem(row, 0, QTableWidgetItem(""))
        self.tabela.setItem(row, 1, QTableWidgetItem(""))

    def remover_linha(self):
        row = self.tabela.currentRow()
        if row >= 0:
            self.tabela.removeRow(row)

    def salvar(self):
        self.agencias.clear()
        for row in range(self.tabela.rowCount()):
            cnpj = self.tabela.item(row, 0).text().strip()
            agencia = self.tabela.item(row, 1).text().strip()
            if cnpj:
                self.agencias[cnpj] = agencia
        self.accept()

# Painel de interface para a renomeação dos arquivos com os estilos já existentes
class PainelOrganizacaoSicoob(QWidget):
    operation_completed = pyqtSignal(str)
    agencias_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.agencias = {}  # Mapeamento: CNPJ -> Agência (ex.: "03.459.850/0033-28": "PA_01")
        self.diretorio = None
        self._dark_mode = False
        self.init_ui()
        self.carregar_agencias()

    def init_ui(self):
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(20, 20, 20, 20)
        self.layout_principal.setSpacing(15)

        self.criar_painel_configuracao()
        self.criar_area_visualizacao()
        self.criar_painel_botoes()
        self.apply_styles(self._dark_mode)

    def apply_styles(self, dark_mode):
        self._dark_mode = dark_mode
        label_style = estilo_label_dark() if dark_mode else estilo_label_light()
        line_style = campo_qline_dark() if dark_mode else campo_qline_light()
        log_style = estilo_log_dark() if dark_mode else estilo_log_light()

        def apply(widget):
            if isinstance(widget, QLabel):
                widget.setStyleSheet(label_style)
            elif isinstance(widget, QLineEdit):
                widget.setStyleSheet(line_style)
            if hasattr(widget, 'children'):
                for child in widget.children():
                    apply(child)
        apply(self)
        for btn in [self.botao_selecionar, self.botao_editar, self.botao_renomear]:
            estilo_hover(btn, dark_mode)
        self.log_unificado.setStyleSheet(log_style)

    def carregar_agencias(self):
        config = configparser.ConfigParser()
        if os.path.exists('sicoob.properties'):
            config.read('sicoob.properties')
            if 'AGENCIAS' in config:
                self.agencias = dict(config['AGENCIAS'].items())
        # Se não houver, inicializa com um exemplo
        if not self.agencias:
            self.agencias = {"03.459.850/0033-28": "PA_01"}
            self.salvar_agencias()

    def log(self, mensagem):
        self.log_unificado.append(f"> {mensagem}")
        self.log_unificado.moveCursor(QTextCursor.MoveOperation.End)

    def criar_painel_configuracao(self):
        self.painel_config = QWidget()
        layout = QHBoxLayout(self.painel_config)
        self.label_pasta = QLabel("Diretório:")
        self.campo_pasta = QLineEdit()
        self.campo_pasta.setReadOnly(True)
        self.botao_selecionar = QPushButton("Selecionar Pasta")
        self.botao_selecionar.setFixedWidth(160)
        self.botao_selecionar.clicked.connect(self.selecionar_pasta)
        self.botao_editar = QPushButton("Lista de Agências")
        self.botao_editar.setFixedWidth(160)
        self.botao_editar.clicked.connect(self.editar_agencias)
        layout.addWidget(self.label_pasta)
        layout.addWidget(self.campo_pasta)
        layout.addWidget(self.botao_selecionar)
        layout.addWidget(self.botao_editar)
        self.layout_principal.addWidget(self.painel_config)

    def criar_area_visualizacao(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.log_unificado = QTextEdit()
        self.log_unificado.setFont(QFont("Consolas", 10))
        self.log_unificado.setReadOnly(True)
        self.log_unificado.setPlaceholderText("Logs do sistema...")
        self.scroll_area.setWidget(self.log_unificado)
        self.layout_principal.addWidget(self.scroll_area)

    def criar_painel_botoes(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        self.botao_renomear = QPushButton("Renomear Arquivos")
        self.botao_renomear.setFixedWidth(160)
        self.label_status = QLabel("Pronto para renomear!")
        layout.addWidget(self.botao_renomear)
        layout.addWidget(self.label_status)
        self.botao_renomear.clicked.connect(self.renomear_arquivos)
        self.layout_principal.addWidget(container)

    def selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if pasta:
            self.diretorio = pasta
            self.campo_pasta.setText(pasta)
            self.atualizar_visualizacao()

    def atualizar_visualizacao(self):
        self.log_unificado.clear()
        if self.diretorio and os.path.exists(self.diretorio):
            try:
                for item in os.listdir(self.diretorio):
                    self.log_unificado.append(item)
            except Exception as e:
                self.log(f"Erro ao listar diretório: {str(e)}")

    def editar_agencias(self):
        editor = EditorAgencias(self.agencias, self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.salvar_agencias()
            self.agencias_updated.emit()
            self.log("Lista de agências atualizada!")

    def salvar_agencias(self):
        config = configparser.ConfigParser()
        config['AGENCIAS'] = self.agencias
        with open('sicoob.properties', 'w') as f:
            config.write(f)

    def renomear_arquivos(self):
        if not self.diretorio:
            self.log("Selecione um diretório primeiro!")
            return
        self.botao_renomear.setEnabled(False)
        self.log("Iniciando renomeação dos arquivos...")
        self.worker = OrganizadorSicoobThread(self.diretorio, self.agencias)
        self.worker.progresso.connect(self.atualizar_progresso)
        self.worker.mensagem.connect(self.log)
        self.worker.error.connect(self.log)
        self.worker.finalizado.connect(self.finalizar_renomeacao)
        self.worker.start()

    def atualizar_progresso(self, valor):
        self.log(f"Progresso: {valor}%")

    def finalizar_renomeacao(self, sucesso):
        if sucesso:
            self.log("Renomeação concluída com sucesso!")
        else:
            self.log("Renomeação finalizada com erros.")
        self.botao_renomear.setEnabled(True)
