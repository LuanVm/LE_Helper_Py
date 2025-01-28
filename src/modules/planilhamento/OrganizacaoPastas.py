from collections import defaultdict
import os
import configparser
import shutil
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QLabel, QTextEdit, QLineEdit, QPushButton, QCheckBox,
    QGridLayout, QVBoxLayout, QHBoxLayout, QFileDialog, QProgressBar,
    QScrollArea, QMessageBox, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtGui import QFont, QTextCursor, QIcon
from utils.GerenEstilos import (
    estilo_label_light, estilo_label_dark,
    campo_qline_light, campo_qline_dark,
    estilo_check_box_light, estilo_check_box_dark,
    estilo_log_light, estilo_log_dark,
    estilo_progress_bar_light, estilo_progress_bar_dark,
    estilo_hover
)

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
        for i, (padrao, nome_pasta) in enumerate(self.clientes.items()):  # Inverte a ordem
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
            padrao = self.tabela.item(row, 0).text().strip()  # Padrão é a chave
            nome_pasta = self.tabela.item(row, 1).text().strip()  # Nome da pasta é o valor
            if padrao:
                self.clientes[padrao] = nome_pasta  # Corrigir a ordem do dicionário
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
        """Aplica os estilos aos componentes com base no modo selecionado"""
        self._dark_mode = dark_mode
        
        # Chamar as funções de estilo para obter os valores
        label_style = estilo_label_dark() if dark_mode else estilo_label_light()
        line_style = campo_qline_dark() if dark_mode else campo_qline_light()
        check_style = estilo_check_box_dark() if dark_mode else estilo_check_box_light()
        log_style = estilo_log_dark() if dark_mode else estilo_log_light()
        progress_style = estilo_progress_bar_dark() if dark_mode else estilo_progress_bar_light()

        # Aplicar estilos recursivamente
        def apply(widget):
            if isinstance(widget, QLabel):
                widget.setStyleSheet(label_style)
            elif isinstance(widget, QLineEdit):
                widget.setStyleSheet(line_style)
            elif isinstance(widget, QCheckBox):
                widget.setStyleSheet(check_style)
            elif isinstance(widget, (QTextEdit, QProgressBar)):
                # Aplicar estilos específicos para esses componentes
                pass
            
            if hasattr(widget, 'children'):
                for child in widget.children():
                    apply(child)

        apply(self)

        for btn in [self.botao_selecionar, self.botao_editar, 
                   self.botao_organizar, self.botao_reverter]:
            estilo_hover(btn, dark_mode)
        
        # Aplicar estilos específicos
        self.log_unificado.setStyleSheet(log_style)
        self.barra_progresso.setStyleSheet(progress_style)

    def carregar_clientes(self):
        """Carrega a lista de clientes do arquivo de configuração"""
        config = configparser.ConfigParser()
        if os.path.exists('clientes.properties'):
            config.read('clientes.properties')
            if 'CLIENTES' in config:
                # Manter a estrutura {padrão: nome_da_pasta}
                self.clientes = dict(config['CLIENTES'].items())
        else:
            # Cria um arquivo padrão se não existir
            self.clientes = {
                'ClienteExemplo': 'CE_'
            }
            self.salvar_clientes()

    def log(self, mensagem):
        """Adiciona mensagem ao log"""
        self.log_unificado.append(f"> {mensagem}")
        self.log_unificado.moveCursor(QTextCursor.MoveOperation.End)

    def criar_painel_configuracao(self):
        self.painel_config = QWidget()
        layout = QGridLayout(self.painel_config)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Componentes de seleção
        self.label_pasta = QLabel("Diretório a ser organizado:")
        self.campo_pasta = QLineEdit()
        self.campo_pasta.setReadOnly(True)

        
        self.botao_selecionar = QPushButton("Selecionar Pasta")
        self.botao_selecionar.setFixedWidth(160)
        self.botao_selecionar.clicked.connect(self.selecionar_pasta)

        # Layout de seleção
        hbox = QHBoxLayout()
        hbox.addWidget(self.label_pasta)
        hbox.addWidget(self.campo_pasta)
        hbox.addWidget(self.botao_selecionar)
        layout.addLayout(hbox, 0, 0, 1, 2)

        # Botão de edição
        self.botao_editar = QPushButton("Lista de Clientes")
        self.botao_editar.setFixedWidth(160)
        self.botao_editar.clicked.connect(self.editar_clientes)
        layout.addWidget(self.botao_editar, 0, 2)

        # Checkboxes
        self.check_subpastas = QCheckBox("Criar e organizar em subpastas")
        self.check_juntar = QCheckBox("Buscar e juntar arquivos em subpastas")
        self.check_subpastas.setChecked(True)
        
        # Conexões
        self.check_subpastas.toggled.connect(self.atualizar_checks)
        self.check_juntar.toggled.connect(self.atualizar_checks)

        layout.addWidget(self.check_subpastas, 1, 0, 1, 3)
        layout.addWidget(self.check_juntar, 2, 0, 1, 3)

        self.layout_principal.addWidget(self.painel_config)

    def conectar_worker(self):
        """Conecta os sinais do worker à interface do usuário"""
        self.worker.progresso.connect(self.barra_progresso.setValue)
        self.worker.mensagem.connect(self.log)
        self.worker.finalizado.connect(self._operacao_finalizada)
        self.worker.error.connect(self._mostrar_erro)
        self.worker.finished.connect(self.worker.deleteLater)

    def _operacao_finalizada(self, sucesso):
        """Atualiza a interface após conclusão da operação"""
        self.botao_organizar.setEnabled(True)
        self.botao_reverter.setEnabled(True)
        self.label_status.setText("Operação concluída com sucesso!" if sucesso else "Operação falhou!")

    def _mostrar_erro(self, mensagem):
        """Exibe mensagens de erro na interface"""
        self.log(f"ERRO: {mensagem}")
        QMessageBox.critical(self, "Erro", mensagem)

    def atualizar_checks(self, checked):
        """Atualiza o estado dos checkboxes para serem mutuamente exclusivos."""
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

        self.botao_reverter = QPushButton("Reverter") #desativado
        self.barra_progresso = QProgressBar() #desativado
        self.label_status = QLabel("Pronto para organizar!")

        layout.addWidget(self.botao_organizar)
        #layout.addWidget(self.botao_reverter)
        #layout.addWidget(self.barra_progresso)
        layout.addWidget(self.label_status)

        self.botao_organizar.clicked.connect(self.iniciar_organizacao)
        self.botao_reverter.clicked.connect(self.reverter_organizacao)

        self.layout_principal.addWidget(container)

    def iniciar_organizacao(self):
        """Inicia a operação de organização com base na seleção do usuário."""
        if self.check_subpastas.isChecked():
            self.organizar_arquivos()
        elif self.check_juntar.isChecked():
            self.juntar_arquivos()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma opção de organização!")

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

        caminho_base = os.path.join(os.path.dirname(__file__), "resources", "icons")
        caminho_icone = os.path.join(caminho_base, "logo.ico")
        if os.path.exists(caminho_icone):
            self.setWindowIcon(QIcon(caminho_icone))
            
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.salvar_clientes()
            self.clientes_updated.emit()
            QMessageBox.information(self, "Sucesso", "Lista de clientes atualizada!")

    def salvar_clientes(self):
        config = configparser.ConfigParser()
        config['CLIENTES'] = self.clientes
        with open('clientes.properties', 'w') as f:
            config.write(f)

    def extrair_cliente(self, nome_arquivo):
        """Retorna o nome da pasta baseado no padrão do arquivo (case-insensitive)"""
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
            QMessageBox.warning(self, "Aviso", "Nenhum cliente encontrado para organização!")
            return

        resposta = QMessageBox.question(
            self, "Confirmar",
            f"Deseja organizar {sum(len(f) for f in preview.values())} arquivos?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if resposta == QMessageBox.StandardButton.Yes:
            self.worker = OrganizadorThread(self.diretorio, self.clientes)
            self.conectar_worker()
            self.worker.start()

    def juntar_arquivos(self):
        resposta = QMessageBox.question(
            self, "Confirmar",
            "Deseja juntar todos os arquivos das subpastas para a pasta principal?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if resposta == QMessageBox.StandardButton.Yes:
            self.worker = AgrupadorThread(self.diretorio)
            self.conectar_worker()
            self.worker.start()

    def reverter_organizacao(self):
        if not self.historico:
            QMessageBox.warning(self, "Aviso", "Nenhuma operação para reverter!")
            return

        resposta = QMessageBox.question(
            self, "Confirmar",
            "Deseja reverter a última operação?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if resposta == QMessageBox.StandardButton.Yes:
            self.worker = ReversorThread(self.diretorio, self.historico)
            self.conectar_worker()
            self.worker.start()

class OrganizadorThread(QThread):
    progresso = pyqtSignal(int)
    mensagem = pyqtSignal(str)
    finalizado = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, diretorio, clientes):
        super().__init__()
        self.diretorio = diretorio
        self.clientes = clientes
        self.historico = []

    def run(self):
        try:
            arquivos = [f for f in os.listdir(self.diretorio) if os.path.isfile(os.path.join(self.diretorio, f))]
            total = len(arquivos)
            pastas_criadas = 0
            arquivos_movidos = 0

            for i, arquivo in enumerate(arquivos):
                if self.isInterruptionRequested():
                    break

                caminho_origem = os.path.join(self.diretorio, arquivo)
                if os.path.basename(caminho_origem).lower() == 'desktop.ini':
                    continue

                cliente = self.extrair_cliente(arquivo)
                if not cliente:
                    continue

                pasta_destino = os.path.join(self.diretorio, cliente)
                if not os.path.exists(pasta_destino):
                    os.makedirs(pasta_destino)
                    pastas_criadas += 1

                caminho_destino = os.path.join(pasta_destino, arquivo)
                if os.path.exists(caminho_destino):
                    caminho_destino = self.gerar_nome_unico(caminho_destino)

                shutil.move(caminho_origem, caminho_destino)
                self.historico.append((caminho_destino, caminho_origem))
                arquivos_movidos += 1

                self.progresso.emit(int((i+1)/total*100))

            self.mensagem.emit(f"Organização concluída! Pastas criadas: {pastas_criadas}, Arquivos movidos: {arquivos_movidos}")
            self.finalizado.emit(True)

        except Exception as e:
            self.error.emit(f"Erro na organização: {str(e)}")
            self.finalizado.emit(False)

    def extrair_cliente(self, nome_arquivo):
        """Retorna o nome da pasta baseado no padrão do arquivo (case-insensitive)"""
        nome_arquivo_lower = nome_arquivo.lower()
        for padrao, nome_pasta in self.clientes.items():
            if padrao and nome_arquivo_lower.startswith(padrao.lower()):
                return nome_pasta
        return ""

    def gerar_nome_unico(self, caminho):
        base, ext = os.path.splitext(caminho)
        contador = 1
        while os.path.exists(caminho):
            caminho = f"{base}_{contador}{ext}"
            contador += 1
        return caminho

class AgrupadorThread(QThread):
    progresso = pyqtSignal(int)
    mensagem = pyqtSignal(str)
    finalizado = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, diretorio):
        super().__init__()
        self.diretorio = diretorio
        self.historico = []

    def run(self):
        try:
            arquivos_processados = 0
            total = sum(len(files) for _, _, files in os.walk(self.diretorio)) - len(os.listdir(self.diretorio))

            for root, dirs, files in os.walk(self.diretorio, topdown=False):
                for file in files:
                    if self.isInterruptionRequested():
                        break

                    caminho_origem = os.path.join(root, file)
                    if root == self.diretorio or os.path.basename(caminho_origem).lower() == 'desktop.ini':
                        continue

                    caminho_destino = os.path.join(self.diretorio, file)
                    if os.path.exists(caminho_destino):
                        caminho_destino = self.gerar_nome_unico(caminho_destino)

                    shutil.move(caminho_origem, caminho_destino)
                    self.historico.append((caminho_destino, caminho_origem))
                    arquivos_processados += 1
                    self.progresso.emit(int((arquivos_processados/total)*100))

                # Remove pastas vazias
                if root != self.diretorio and not os.listdir(root):
                    os.rmdir(root)

            self.mensagem.emit(f"Junção concluída! Arquivos movidos: {arquivos_processados}")
            self.finalizado.emit(True)

        except Exception as e:
            self.error.emit(f"Erro no agrupamento: {str(e)}")
            self.finalizado.emit(False)

class ReversorThread(QThread):
    progresso = pyqtSignal(int)
    mensagem = pyqtSignal(str)
    finalizado = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, diretorio, historico):
        super().__init__()
        self.diretorio = diretorio
        self.historico = historico

    def run(self):
        try:
            total = len(self.historico)
            for i, (destino, origem) in enumerate(reversed(self.historico)):
                if self.isInterruptionRequested():
                    break

                if os.path.exists(destino):
                    shutil.move(destino, origem)
                    pasta = os.path.dirname(destino)
                    if not os.listdir(pasta):
                        os.rmdir(pasta)

                self.progresso.emit(int((i+1)/total*100))

            self.mensagem.emit("Reversão concluída com sucesso!")
            self.finalizado.emit(True)

        except Exception as e:
            self.error.emit(f"Erro na reversão: {str(e)}")
            self.finalizado.emit(False)