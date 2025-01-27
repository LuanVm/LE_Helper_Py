import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QScrollArea, QGridLayout
)

from utils.GerenEstilos import (
    estilo_label_light, estilo_label_dark,
    campo_qline_light, campo_qline_dark,
    estilo_hover, estilo_log_light, estilo_log_dark
)

class PainelSubstituicaoSimples(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(20, 20, 20, 20)
        self.layout().setSpacing(10)

        self._create_input_panel()
        self._create_file_view()

    def _create_input_panel(self):
        input_panel = QWidget()
        input_layout = QGridLayout(input_panel)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        self.text_pasta = self._create_input_line("Pasta:", input_layout, 0)
        self.text_original = self._create_input_line("Nome Original:", input_layout, 1)
        self.text_nova = self._create_input_line("Alterar Para:", input_layout, 2)

        self.btn_selecionar = QPushButton("Selecionar Pasta")
        self.btn_renomear = QPushButton("Renomear")

        input_layout.addWidget(self.btn_selecionar, 3, 0)
        input_layout.addWidget(self.btn_renomear, 3, 2)

        self.btn_selecionar.clicked.connect(self.selecionar_pasta)
        self.btn_renomear.clicked.connect(self.renomear_arquivos)

        info_label = QLabel("Lembrando que a aplicação respeita caracteres em caixa alta.")
        info_label.setStyleSheet("color: gray;")
        input_layout.addWidget(info_label, 4, 0, 1, 3)

        self.layout().addWidget(input_panel)

    def _create_input_line(self, label_text, layout, row):
        label = QLabel(label_text)
        label.setStyleSheet(estilo_label_light() if not self.is_dark_mode else estilo_label_dark())  # Aplicando o estilo do label
        text_field = QLineEdit()
        text_field.setStyleSheet(campo_qline_light() if not self.is_dark_mode else campo_qline_dark())  # Aplicando o estilo do campo
        layout.addWidget(label, row, 0)
        layout.addWidget(text_field, row, 1, 1, 2)
        return text_field

    def _create_file_view(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.text_area_arquivos = QTextEdit()
        self.text_area_arquivos.setReadOnly(True)
        self.text_area_arquivos.setStyleSheet(estilo_log_light() if not self.is_dark_mode else estilo_log_dark())  # Estilo para a área de texto
        scroll_area.setWidget(self.text_area_arquivos)

        self.layout().addWidget(scroll_area)

    def apply_styles(self, is_dark_mode):
        self.is_dark_mode = is_dark_mode
        styles = {
            'label': estilo_label_dark() if is_dark_mode else estilo_label_light(),
            'line': campo_qline_dark() if is_dark_mode else campo_qline_light(),
        }

        for label in self.findChildren(QLabel):
            label.setStyleSheet(styles['label'])

        for line_edit in self.findChildren(QLineEdit):
            line_edit.setStyleSheet(styles['line'])

        for btn in [self.btn_selecionar, self.btn_renomear]:
            estilo_hover(btn, is_dark_mode)

    def selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if pasta:
            self.text_pasta.setText(pasta)
            self.atualizar_visualizacao_arquivos(pasta)

    def renomear_arquivos(self):
        pasta = self.text_pasta.text()
        if not os.path.isdir(pasta):
            self.exibir_mensagem("Pasta inválida ou vazia.", QMessageBox.Icon.Critical)
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
