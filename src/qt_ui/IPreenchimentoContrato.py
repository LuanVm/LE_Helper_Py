import os
from pathlib import Path
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QFormLayout, QFileDialog, QTabWidget, QScrollArea,
    QHBoxLayout, QSizePolicy
)
from services.PreenchimentoContrato import ContratoWorker
from utils.sheetStyles import (
    estilo_label_light, estilo_label_dark,
    campo_qline_light, campo_qline_dark,
    estilo_hover
)

class PainelPreenchimentoContrato(QWidget):
    processStarted = pyqtSignal()
    processFinished = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_path = self._get_default_template()
        self._dark_mode = False  # Será alterado externamente via themeManager
        # Lista de campos obrigatórios
        self.campos_obrigatorios = [
            'razao_social', 'cnpj', 'endereco_empresa',
            'rep1_nome', 'rep1_cpf', 'rep1_rg', 'rep1_endereco'
        ]
        self.init_ui()
        self.apply_styles(self._dark_mode)

    def _get_default_template(self):
        base_dir = Path(__file__).resolve().parent.parent
        return str(base_dir / "templates" / "modelo_contrato.docx")

    def init_ui(self):
        # Margens e espaçamentos gerais reduzidos para um layout mais compacto
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(10, 10, 10, 10)
        self.layout_principal.setSpacing(10)

        # Seção de seleção de template
        self.criar_secao_template()

        # Criação das abas de formulário
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                font-family: 'Segoe UI';
                font-size: 13px;
                padding: 6px 10px;
                border: 1px solid transparent;
                border-bottom: none;
                background: transparent;
            }
            QTabBar::tab:selected {
                border-color: #ff8c00;
                background-color: rgba(255, 140, 0, 0.15);
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        self._criar_abas()
        self.layout_principal.addWidget(self.tabs)

        # Área de status
        self.criar_area_status()

        # Botões de ação
        self.criar_botoes_acao()

    def criar_secao_template(self):
        layout_template = QHBoxLayout()
        self.lbl_template = QLabel("Modelo selecionado: ")
        self.lbl_template.setObjectName("lbl_template")
        self.btn_template = QPushButton("Selecionar Modelo DOCX")
        self.btn_template.clicked.connect(self.selecionar_template)
        estilo_hover(self.btn_template, self._dark_mode)
        layout_template.addWidget(self.lbl_template)
        layout_template.addWidget(self.btn_template)
        self.layout_principal.addLayout(layout_template)

    def _criar_abas(self):
        self.aba_empresa = self.criar_aba_empresa()
        self.aba_rep1 = self.criar_aba_representante(1)
        self.aba_rep2 = self.criar_aba_representante(2)
        self.tabs.addTab(self.aba_empresa, "Dados Empresariais")
        self.tabs.addTab(self.aba_rep1, "Representante Legal 1")
        self.tabs.addTab(self.aba_rep2, "Representante Legal 2")

    def criar_aba_empresa(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form_layout = QFormLayout(content)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(5)
        campos = [
            ("RAZÃO SOCIAL *", "razao_social"),
            ("CNPJ *", "cnpj"),
            ("ENDEREÇO COMPLETO *", "endereco_empresa")
        ]
        for label_text, key in campos:
            lbl = QLabel(label_text)
            inp = QLineEdit()
            erro = QLabel()
            erro.setVisible(False)
            erro.setObjectName(f"erro_{key}")
            setattr(self, f"inp_{key}", inp)
            setattr(self, f"erro_{key}", erro)
            form_layout.addRow(lbl, inp)
            form_layout.addRow("", erro)
        scroll.setWidget(content)
        return scroll

    def criar_aba_representante(self, num_rep):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form_layout = QFormLayout(content)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(5)
        campos = [
            (f"NOME REP. LEGAL {num_rep} *", f"rep{num_rep}_nome"),
            ("NACIONALIDADE", f"rep{num_rep}_nacionalidade"),
            ("ESTADO CIVIL", f"rep{num_rep}_estado_civil"),
            ("PROFISSÃO", f"rep{num_rep}_profissao"),
            ("CPF *", f"rep{num_rep}_cpf"),
            ("RG *", f"rep{num_rep}_rg"),
            ("ÓRGÃO EMISSOR", f"rep{num_rep}_orgao_emissor"),
            ("E-MAIL", f"rep{num_rep}_email"),
            ("ENDEREÇO *", f"rep{num_rep}_endereco")
        ]
        for label_text, key in campos:
            lbl = QLabel(label_text)
            inp = QLineEdit()
            erro = QLabel()
            erro.setVisible(False)
            erro.setObjectName(f"erro_{key}")
            setattr(self, f"inp_{key}", inp)
            setattr(self, f"erro_{key}", erro)
            form_layout.addRow(lbl, inp)
            form_layout.addRow("", erro)
        scroll.setWidget(content)
        return scroll

    def criar_area_status(self):
        self.status_bar = QLabel()
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.status_bar.setVisible(False)
        self.layout_principal.addWidget(self.status_bar)

    def criar_botoes_acao(self):
        layout_botoes = QHBoxLayout()
        self.btn_processar = QPushButton("Gerar Contrato PDF")
        self.btn_processar.clicked.connect(self.validar_e_processar)
        estilo_hover(self.btn_processar, self._dark_mode)
        layout_botoes.addStretch()
        layout_botoes.addWidget(self.btn_processar)
        self.layout_principal.addLayout(layout_botoes)

    def apply_styles(self, dark_mode):
        self._dark_mode = dark_mode
        cor_erro = "#ff4444" if dark_mode else "#cc0000"
        cor_status = "#4CAF50" if dark_mode else "#2E7D32"

        for label in self.findChildren(QLabel):
            if label.objectName().startswith("erro_"):
                label.setStyleSheet(f"color: {cor_erro}; font-size: 11px;")
            else:
                label.setStyleSheet(estilo_label_dark() if dark_mode else estilo_label_light())

        for campo in self.findChildren(QLineEdit):
            campo.setStyleSheet(campo_qline_dark() if dark_mode else campo_qline_light())

        self.status_bar.setStyleSheet(f"""
            background-color: {cor_status if dark_mode else '#C8E6C9'};
            color: {'#ffffff' if dark_mode else '#1B5E20'};
            padding: 8px;
            border-radius: 4px;
        """)

        for btn in [self.btn_template, self.btn_processar]:
            estilo_hover(btn, dark_mode)

    def selecionar_template(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Modelo DOCX",
            str(Path.home()),
            "Word Documents (*.docx)"
        )
        if file:
            self.template_path = file
            self.lbl_template.setText(f"Modelo selecionado: {Path(file).name}")
            self.mostrar_status("Modelo atualizado com sucesso!", "sucesso")

    def validar_campos(self):
        valido = True
        dados = {}
        for key in self.campos_obrigatorios:
            campo = getattr(self, f"inp_{key}")
            erro = getattr(self, f"erro_{key}")
            if not campo.text().strip():
                erro.setText("Este campo é obrigatório")
                erro.setVisible(True)
                valido = False
            else:
                erro.setVisible(False)
                dados[key] = campo.text().strip()
        return valido, dados

    def mostrar_status(self, mensagem, tipo="erro"):
        cores = {
            "erro": ("#ffebee", "#b71c1c") if self._dark_mode else ("#ffcdd2", "#c62828"),
            "sucesso": ("#e8f5e9", "#1b5e20") if self._dark_mode else ("#c8e6c9", "#2e7d32"),
            "info": ("#e3f2fd", "#0d47a1") if self._dark_mode else ("#bbdefb", "#1565c0")
        }
        self.status_bar.setStyleSheet(f"""
            background-color: {cores[tipo][0]};
            color: {cores[tipo][1]};
            padding: 8px;
            border-radius: 4px;
            border: 1px solid {cores[tipo][1]};
        """)
        self.status_bar.setText(mensagem)
        self.status_bar.setVisible(True)

    def validar_e_processar(self):
        valido, dados = self.validar_campos()
        if not valido:
            self.mostrar_status("Preencha todos os campos obrigatórios marcados em vermelho", "erro")
            self.tabs.setCurrentIndex(0)
            return
        output_dir = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Saída")
        if not output_dir:
            return
        self.processar_contrato(dados, output_dir)

    def processar_contrato(self, dados, output_dir):
        self.worker = ContratoWorker(self.template_path, dados, output_dir)
        self.worker.progress.connect(self.atualizar_progresso)
        self.worker.finished.connect(self.finalizar_processo)
        self.worker.error.connect(self.mostrar_erro)
        self.worker.start()
        self.btn_processar.setEnabled(False)
        self.mostrar_status("Processando contrato...", "info")

    def atualizar_progresso(self, percentual):
        self.status_bar.setText(f"Processando... {percentual}% concluído")

    def finalizar_processo(self, caminho_pdf):
        self.btn_processar.setEnabled(True)
        self.mostrar_status(f"Contrato gerado com sucesso: {caminho_pdf}", "sucesso")
        self.resetar_formulario()

    def mostrar_erro(self, mensagem):
        self.btn_processar.setEnabled(True)
        self.mostrar_status(f"Erro: {mensagem}", "erro")

    def resetar_formulario(self):
        for campo in self.findChildren(QLineEdit):
            campo.clear()
        for erro in self.findChildren(QLabel):
            if erro.objectName().startswith("erro_"):
                erro.setVisible(False)