import configparser
import os
from collections import defaultdict
from pathlib import Path
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QLabel, QTextEdit, QLineEdit, QPushButton, QCheckBox,
    QGridLayout, QVBoxLayout, QHBoxLayout, QFileDialog,
    QScrollArea, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtGui import QFont, QTextCursor, QIcon
from utils.sheetStyles import (
    estilo_label_light, estilo_label_dark,
    campo_qline_light, campo_qline_dark,
    estilo_check_box_light, estilo_check_box_dark,
    estilo_log_light, estilo_log_dark,
    estilo_hover
)
from services.OrganizacaoPastas import OrganizadorThread, AgrupadorThread


class EditorClientes(QDialog):
    def __init__(self, clientes, parent=None):
        super().__init__(parent)
        self.clientes = clientes
        self.setWindowTitle("Editor de Clientes")
        self.setFixedSize(400, 300)
        
        caminho_base = os.path.join(os.path.dirname(__file__), "resources", "icons")
        caminho_icone = os.path.join(caminho_base, "logo.ico")
        if os.path.exists(caminho_icone):
            self.setWindowIcon(QIcon(caminho_icone))
        
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(2)
        self.tabela.setHorizontalHeaderLabels(["Padrão Arquivo", "Nome da Pasta"])
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
        self.tabela.setRowCount(len(self.clientes))
        for i, (padrao, nome_pasta) in enumerate(self.clientes.items()):
            self.tabela.setItem(i, 0, QTableWidgetItem(padrao))
            self.tabela.setItem(i, 1, QTableWidgetItem(nome_pasta))

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
        self.clientes.clear()
        for row in range(self.tabela.rowCount()):
            padrao = self.tabela.item(row, 0).text().strip()
            nome_pasta = self.tabela.item(row, 1).text().strip()
            if padrao:
                self.clientes[padrao] = nome_pasta
        self.accept()


class PainelOrganizacaoPastas(QWidget):
    operation_completed = pyqtSignal(str)
    clientes_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clientes = {}
        self.diretorio = None
        self._dark_mode = False
        self.historico = []
        self.init_ui()
        self.carregar_clientes()

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
        check_style = estilo_check_box_dark() if dark_mode else estilo_check_box_light()
        log_style = estilo_log_dark() if dark_mode else estilo_log_light()

        def apply(widget):
            if isinstance(widget, QLabel):
                widget.setStyleSheet(label_style)
            elif isinstance(widget, QLineEdit):
                widget.setStyleSheet(line_style)
            elif isinstance(widget, QCheckBox):
                widget.setStyleSheet(check_style)
            
            if hasattr(widget, 'children'):
                for child in widget.children():
                    apply(child)

        apply(self)

        for btn in [self.botao_selecionar, self.botao_editar, self.botao_organizar]:
            estilo_hover(btn, dark_mode)
        
        self.log_unificado.setStyleSheet(log_style)

    def carregar_clientes(self):
        config = configparser.ConfigParser()
        if os.path.exists('clientes.properties'):
            config.read('clientes.properties')
            if 'CLIENTES' in config:
                self.clientes = dict(config['CLIENTES'].items())
        else:
            self.clientes = {'ClienteExemplo': 'CE_'}
            self.salvar_clientes()
            self.log("📝 Arquivo de clientes criado com configurações padrão")

    def log(self, mensagem):
        self.log_unificado.append(f"<span style='color: {'#e0e0e0' if self._dark_mode else '#333333'}'>{mensagem}</span>")
        self.log_unificado.moveCursor(QTextCursor.MoveOperation.End)

    def criar_painel_configuracao(self):
        self.painel_config = QWidget()
        layout = QGridLayout(self.painel_config)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        self.label_pasta = QLabel("Diretório a ser organizado:")
        self.campo_pasta = QLineEdit()
        self.campo_pasta.setReadOnly(True)
        
        self.botao_selecionar = QPushButton("Selecionar Pasta")
        self.botao_selecionar.setFixedWidth(160)
        self.botao_selecionar.clicked.connect(self.selecionar_pasta)

        hbox = QHBoxLayout()
        hbox.addWidget(self.label_pasta)
        hbox.addWidget(self.campo_pasta)
        hbox.addWidget(self.botao_selecionar)
        layout.addLayout(hbox, 0, 0, 1, 2)

        self.botao_editar = QPushButton("Lista de Clientes")
        self.botao_editar.setFixedWidth(160)
        self.botao_editar.clicked.connect(self.editar_clientes)
        layout.addWidget(self.botao_editar, 0, 2)

        self.check_subpastas = QCheckBox("Criar e organizar em subpastas")
        self.check_juntar = QCheckBox("Buscar e juntar arquivos em subpastas")
        self.check_subpastas.setChecked(True)
        
        self.check_subpastas.toggled.connect(self.atualizar_checks)
        self.check_juntar.toggled.connect(self.atualizar_checks)

        layout.addWidget(self.check_subpastas, 1, 0, 1, 3)
        layout.addWidget(self.check_juntar, 2, 0, 1, 3)

        self.layout_principal.addWidget(self.painel_config)

    def conectar_worker(self):
        self.worker.mensagem.connect(self.log)
        self.worker.finalizado.connect(self._operacao_finalizada)
        self.worker.error.connect(self._mostrar_erro)
        self.worker.finished.connect(self.worker.deleteLater)

    def _operacao_finalizada(self, sucesso):
        self.botao_organizar.setEnabled(True)
        if sucesso:
            self.log("✅ Operação concluída com sucesso!")
        else:
            self.log("⛔ Operação falhou!")

    def _mostrar_erro(self, mensagem):
        self.log(f"⛔ ERRO: {mensagem}")

    def atualizar_checks(self, checked):
        sender = self.sender()
        if sender == self.check_subpastas and checked:
            self.check_juntar.setChecked(False)
        elif sender == self.check_juntar and checked:
            self.check_subpastas.setChecked(False)

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
        
        self.botao_organizar = QPushButton("Organizar")
        self.botao_organizar.setFixedWidth(160)
        self.botao_organizar.clicked.connect(self.iniciar_organizacao)

        self.label_status = QLabel("Pronto para organizar!")

        layout.addWidget(self.botao_organizar)
        layout.addWidget(self.label_status)
        self.layout_principal.addWidget(container)

    def iniciar_organizacao(self):
        if self.check_subpastas.isChecked():
            self.organizar_arquivos()
        elif self.check_juntar.isChecked():
            self.juntar_arquivos()
        else:
            self.log("⚠️ Selecione uma opção de organização!")

    def selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if pasta:
            self.diretorio = pasta
            self.campo_pasta.setText(pasta)
            self.log(f"📂 Pasta selecionada: {os.path.basename(pasta)}")
            self.atualizar_visualizacao()

    def atualizar_visualizacao(self):
        self.log_unificado.clear()
        if self.diretorio and os.path.exists(self.diretorio):
            try:
                for item in os.listdir(self.diretorio):
                    self.log_unificado.append(item)
            except Exception as e:
                self.log(f"⛔ Erro ao listar diretório: {str(e)}")

    def gerar_previa(self):
        preview = defaultdict(list)
        if self.diretorio and os.path.exists(self.diretorio):
            for arquivo in os.listdir(self.diretorio):
                caminho_completo = os.path.join(self.diretorio, arquivo)
                if os.path.isfile(caminho_completo):
                    cliente = self.extrair_cliente(arquivo)
                    preview[cliente].append(arquivo)
        return preview

    def editar_clientes(self):
        editor = EditorClientes(self.clientes, self)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.salvar_clientes()
            self.clientes_updated.emit()
            self.log("✅ Lista de clientes atualizada!")

    def salvar_clientes(self):
        config = configparser.ConfigParser()
        config['CLIENTES'] = self.clientes
        with open('clientes.properties', 'w') as f:
            config.write(f)
        self.log("💾 Configurações salvas com sucesso")

    def extrair_cliente(self, nome_arquivo):
        nome_arquivo_lower = nome_arquivo.lower()
        for padrao, nome_pasta in self.clientes.items():
            if padrao and nome_arquivo_lower.startswith(padrao.lower()):
                return nome_pasta
        return ""

    def organizar_arquivos(self):
        caminho_base = os.path.join(os.path.dirname(__file__), "resources", "icons")
        caminho_icone = os.path.join(caminho_base, "logo.ico")
        if os.path.exists(caminho_icone):
            self.setWindowIcon(QIcon(caminho_icone))
    
        preview = self.gerar_previa()
        if not preview:
            self.log("⚠️ Nenhum cliente encontrado para organização!")
            return
    
        self.worker = OrganizadorThread(self.diretorio, self.clientes)
        self.conectar_worker()
        self.worker.start()
        self.log("⏳ Iniciando organização de arquivos...")

    def juntar_arquivos(self):
        self.worker = AgrupadorThread(self.diretorio)
        self.conectar_worker()
        self.worker.start()
        self.log("⏳ Iniciando agrupamento de arquivos...")