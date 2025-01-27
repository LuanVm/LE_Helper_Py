import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QScrollArea
)
from PyQt6.QtGui import QIcon
from utils.GerenEstilos import (
    estilo_label_light, estilo_label_dark, campo_qline_light, campo_qline_dark,
    estilo_hover, estilo_log_light, estilo_log_dark
)

class PainelSubstituicaoSimples(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(15, 15, 15, 15)
        self.layout().setSpacing(15)

        self._create_input_controls()
        self._create_file_view()

    def _create_input_controls(self):
        grid = QGridLayout()
        grid.setVerticalSpacing(10)
        grid.setHorizontalSpacing(15)
        grid.setColumnStretch(1, 1)

        # Pasta de entrada
        self.label_pasta = QLabel("Pasta:")
        self.text_pasta = QLineEdit()
        self.text_pasta.setReadOnly(True)
        self.btn_selecionar = QPushButton("Selecionar Pasta")
        self.btn_selecionar.setFixedSize(160, 32)
        self.btn_selecionar.clicked.connect(self.selecionar_pasta)

        # Nome do arquivo original
        self.label_original = QLabel("Nome Original:")
        self.text_original = QLineEdit()

        self.btn_renomear = QPushButton("Renomear")
        self.btn_renomear.setFixedSize(160, 32)
        self.btn_renomear.clicked.connect(self.renomear_arquivos)

        # Nome do arquivo alterado
        self.label_nova = QLabel("Alterar Para:")
        self.text_nova = QLineEdit()

        # Adicionando elementos ao layout
        grid.addWidget(self.label_pasta, 0, 0)
        grid.addWidget(self.text_pasta, 0, 1)
        grid.addWidget(self.btn_selecionar, 0, 2)

        grid.addWidget(self.label_original, 1, 0)
        grid.addWidget(self.text_original, 1, 1)
        grid.addWidget(self.btn_renomear, 1, 2)

        grid.addWidget(self.label_nova, 2, 0, 1, 1)
        grid.addWidget(self.text_nova, 2, 1)

        self.layout().addLayout(grid)

    def _create_file_view(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.text_area_arquivos = QTextEdit()
        self.text_area_arquivos.setReadOnly(True)
        scroll_area.setWidget(self.text_area_arquivos)

        self.layout().addWidget(scroll_area)

    def apply_styles(self, is_dark_mode):
        self.is_dark_mode = is_dark_mode
        label_style = estilo_label_dark() if is_dark_mode else estilo_label_light()
        line_style = campo_qline_dark() if is_dark_mode else campo_qline_light()
        log_style = estilo_log_dark() if is_dark_mode else estilo_log_light()

        for label in [self.label_pasta, self.label_original, self.label_nova]:
            label.setStyleSheet(label_style)
        for line_edit in [self.text_pasta, self.text_original, self.text_nova]:
            line_edit.setStyleSheet(line_style)
        for log_area in [self.text_area_arquivos]:
            log_area.setStyleSheet(log_style)

        # Aplica estilo nos botões
        estilo_hover(self.btn_selecionar, is_dark_mode)
        estilo_hover(self.btn_renomear, is_dark_mode)

    def selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if pasta:
            self.text_pasta.setText(pasta)
            self.atualizar_visualizacao_arquivos(pasta)

    def renomear_arquivos(self):
        pasta = self.text_pasta.text()

        if not os.path.isdir(pasta):
            self.exibir_mensagem("Pasta inválida ou vazia.", QMessageBox.Icon.Information)
            return

        palavra_antiga = self.text_original.text()
        palavra_nova = self.text_nova.text()

        erro_ao_renomear = False
        for nome_arquivo in os.listdir(pasta):
            caminho_antigo = os.path.join(pasta, nome_arquivo)
            if os.path.isfile(caminho_antigo):
                novo_nome = nome_arquivo.replace(palavra_antiga, palavra_nova)
                caminho_novo = os.path.join(pasta, novo_nome)
                try:
                    os.rename(caminho_antigo, caminho_novo)
                except Exception as e:
                    erro_ao_renomear = True
                    print(f"Erro ao renomear {nome_arquivo}: {e}")

        mensagem = "Renomeação concluída com erros." if erro_ao_renomear else "Renomeação concluída!"
        tipo_mensagem = QMessageBox.Icon.Warning if erro_ao_renomear else QMessageBox.Icon.Information
        self.exibir_mensagem(mensagem, tipo_mensagem)
        self.atualizar_visualizacao_arquivos(pasta)

    def atualizar_visualizacao_arquivos(self, pasta):
        self.text_area_arquivos.clear()
        if os.path.isdir(pasta):
            arquivos = sorted([f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))])
            self.text_area_arquivos.setPlainText("\n".join(arquivos))

    def exibir_mensagem(self, mensagem, tipo):
        msg_box = QMessageBox(self)
        msg_box.setIcon(tipo)
        msg_box.setText(mensagem)
        msg_box.setWindowTitle("Mensagem")
        msg_box.exec()
