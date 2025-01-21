import gc
import os
import time
import unicodedata
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit,
    QFileDialog, QProgressBar, QTextEdit, QCheckBox,
    QMessageBox, QLabel, QSizePolicy, QHBoxLayout
)
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot, QSettings, Qt
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment, NamedStyle

# Importa os estilos visuais
from GerenEstilos import (
    estilo_label_light, estilo_label_dark,
    campo_qline_light, campo_qline_dark,
    estilo_check_box_light, estilo_check_box_dark,
    estilo_log_light, estilo_log_dark,
    estilo_progress_bar_light, estilo_progress_bar_dark,
    estilo_hover, estilo_sheet_light, estilo_sheet_dark
)

class PainelProcessamentoAgitel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False  # Começa no modo claro
        self.init_ui()

    def init_ui(self):
        """Monta a interface do usuário"""
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(15, 15, 15, 15)
        self.layout().setSpacing(15)

        # Cria os componentes da tela
        self._create_file_controls()
        self._create_progress_bar()
        self._create_results_area()

    def _create_file_controls(self):
        """Monta a área de seleção de arquivo"""
        grid = QGridLayout()
        grid.setVerticalSpacing(10)
        grid.setHorizontalSpacing(15)
        grid.setColumnStretch(1, 1)  # Faz a coluna do arquivo expandir

        # Texto e campo do arquivo
        self.label_file = QLabel("Arquivo XLSX (Planilha da Agitel):")
        self.text_file = QLineEdit()
        self.text_file.setReadOnly(True)  # Só permite seleção por diálogo

        # Botões com tamanho igual
        self.btn_select_file = QPushButton("Selecionar Arquivo")
        self.btn_process = QPushButton("Processar")
        
        # Configura tamanho dos botões
        for btn in [self.btn_select_file, self.btn_process]:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setMinimumWidth(160)  # Largura mínima igual

        # Organiza os botões lado a lado
        button_container = QHBoxLayout()
        button_container.addWidget(self.btn_select_file)
        button_container.addWidget(self.btn_process)
        button_container.setSpacing(10)

        # Checkbox alinhado embaixo do botão Processar
        self.checkbox_equalize = QCheckBox("Equalizar 'Região'")

        # Posiciona os elementos na tela
        grid.addWidget(self.label_file, 0, 0)
        grid.addWidget(self.text_file, 0, 1)
        grid.addLayout(button_container, 0, 2)
        grid.addWidget(self.checkbox_equalize, 0, 3, 1, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.layout().addLayout(grid)
        self.btn_select_file.clicked.connect(self.select_file)
        self.btn_process.clicked.connect(self.process_file)

    def _create_progress_bar(self):
        """Cria a barra de progresso"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)  # Começa zerada
        self.layout().addWidget(self.progress_bar)

    def _create_results_area(self):
        """Área de exibição dos resultados"""
        self.text_results = QTextEdit()
        self.text_results.setReadOnly(True)  # Só leitura
        self.text_results.setPlaceholderText("Resultados do processamento...")
        self.layout().addWidget(self.text_results)

    def apply_styles(self, is_dark_mode):
        """Aplica os temas claro/escuro"""
        self.is_dark_mode = is_dark_mode
        
        # Escolhe os estilos conforme o tema
        label_style = estilo_label_dark() if is_dark_mode else estilo_label_light()
        line_style = campo_qline_dark() if is_dark_mode else campo_qline_light()
        check_style = estilo_check_box_dark() if is_dark_mode else estilo_check_box_light()
        log_style = estilo_log_dark() if is_dark_mode else estilo_log_light()
        progress_style = estilo_progress_bar_dark() if is_dark_mode else estilo_progress_bar_light()

        # Aplica os estilos nos componentes
        self.label_file.setStyleSheet(label_style)
        self.text_file.setStyleSheet(line_style)
        self.checkbox_equalize.setStyleSheet(check_style)
        self.text_results.setStyleSheet(log_style)
        self.progress_bar.setStyleSheet(progress_style)

        # Efeito hover nos botões
        for button in [self.btn_select_file, self.btn_process]:
            estilo_hover(button)

    def select_file(self):
        """Abre o diálogo para escolher arquivo"""
        settings = QSettings("LivreEscolha", "LE_Helper")
        last_dir = settings.value("last_open_dir", "")  # Pega último diretório
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo Excel", last_dir, "Excel Files (*.xlsx)"
        )
        
        if file_path:
            self.text_file.setText(file_path)
            settings.setValue("last_open_dir", os.path.dirname(file_path))  # Salva novo diretório

    def process_file(self):
        """Inicia o processamento do arquivo"""
        file_path = self.text_file.text()
        if not self._validate_file(file_path):
            return

        self.progress_bar.reset()
        equalize = self.checkbox_equalize.isChecked()  # Verifica se precisa equalizar
        
        # Cria e inicia a thread de processamento
        self.processor = ProcessarArquivo(file_path, equalize)
        self.processor.progress.connect(self.update_progress)
        self.processor.finished.connect(self.process_finished)
        self.processor.start()

    def _validate_file(self, file_path):
        """Valida se o arquivo é OK"""
        if not file_path:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo Excel.")
            return False
        if not os.path.isfile(file_path):
            QMessageBox.warning(self, "Aviso", "Arquivo inválido.")
            return False
        return True

    @pyqtSlot(int)
    def update_progress(self, value):
        """Atualiza a barra de progresso"""
        self.progress_bar.setValue(value)

    @pyqtSlot(str)
    def process_finished(self, message):
        """Exibe mensagem final no log"""
        base_color = "#e0e0e0" if self.is_dark_mode else "#333333"
        self.text_results.append(f'<span style="color: {base_color}">{message}</span>')

class ProcessarArquivo(QThread):
    """Thread para processamento pesado de Excel"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    # Constantes de colunas alinhadas com o Java
    COLUNA_DATA = 0
    COLUNA_ORIGEM = 1
    COLUNA_SERVICO = 2
    COLUNA_REGIAO = 3
    COLUNA_DESTINO = 4
    COLUNA_DURACAO = 5
    COLUNA_DURACAO_MINUTOS = 6
    COLUNA_VALOR = 7

    def __init__(self, file_path, equalize):
        super().__init__()
        self.file_path = file_path
        self.equalize = equalize
        self.general_style = NamedStyle(name="general")
        self.date_style = NamedStyle(name="date")
        self.accounting_style = NamedStyle(name="accounting")
        self.minutes_style = NamedStyle(name="minutes")

    def run(self):
        try:
            wb = load_workbook(self.file_path, read_only=not self.equalize)
            output_wb = Workbook()
            output_sheet = output_wb.active
            
            self.create_header(output_sheet)
            self.define_styles(output_wb)

            total_sheets = len(wb.sheetnames)
            self.finished.emit("Iniciando processamento...")

            for idx, sheet_name in enumerate(wb.sheetnames[1:], 1):
                sheet = wb[sheet_name]
                self.finished.emit(f"Processando: {sheet_name}")
                self.process_sheet(sheet, output_sheet)
                
                progress = int((idx / total_sheets) * 100)
                self.progress.emit(progress)

            if self.equalize:
                self.equalize_regiao(output_sheet)

            # Aplica o estilo de minutos após todo o processamento
            for row in output_sheet.iter_rows(min_row=2):
                row[self.COLUNA_DURACAO_MINUTOS].style = self.minutes_style

            output_path = os.path.splitext(self.file_path)[0] + "_leitura_agitel.xlsx"
            output_wb.save(output_path)
            self.progress.emit(100)
            self.finished.emit("Processamento concluído com sucesso!")

        except Exception as e:
            self.finished.emit(f"Erro crítico: {str(e)}")
        finally:
            if 'wb' in locals():
                wb.close()
            if 'output_wb' in locals():
                output_wb.close()
            gc.collect()

    def convert_duration(self, time_val):
        """Converte tempo no formato HH:MM:SS para minutos decimais com 1 casa decimal"""
        try:
            print(f"Valor recebido: {time_val}")  # Log para depuração
            if isinstance(time_val, str):
                partes = time_val.split(':')
                if len(partes) != 3:
                    return 0.0
                horas = int(partes[0])
                minutos = int(partes[1])
                segundos = int(partes[2])
            else:
                return 0.0

            total_minutos = (horas * 60) + minutos + (segundos / 60)
            return round(total_minutos, 1)

        except Exception as e:
            self.finished.emit(f"Erro na conversão: {str(e)}")
            return 0.0

    def create_header(self, sheet):
        """Cria cabeçalho alinhado com o Java"""
        header = [
            "Data", "Origem", "Servico", 
            "Regiao", "Destino", "Duracao", 
            "Duração (minutos)", "Valor"
        ]
        sheet.append(header)
        
        # Formatação do cabeçalho
        for cell in sheet[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')

    def normalize_header(self, header_name):
        """Normalização robusta de nomes de coluna"""
        normalized = unicodedata.normalize('NFKD', str(header_name).strip().lower())
        return ''.join([c for c in normalized if not unicodedata.combining(c)])

    def find_header_row(self, sheet):
        """Encontra a linha de cabeçalho pela coluna Data"""
        for row in sheet.iter_rows(min_row=1, max_row=10):
            try:
                if self.normalize_header(row[0].value) == "data":
                    return row
            except:
                continue
        return None

    def process_sheet(self, sheet, output_sheet):
        header_row = self.find_header_row(sheet)
        if not header_row:
            return

        headers = [self.normalize_header(cell.value) for cell in header_row]
        column_map = {
            "data": ["data"],
            "origem": ["origem", "setor"],
            "servico": ["servico", "identificador"],
            "regiao": ["regiao", "região"],
            "destino": ["destino", "numero_destino"],
            "duracao": ["duracao", "duração"],
            "preco": ["preco", "valor"]
        }

        indices = {}
        for key, aliases in column_map.items():
            for alias in aliases:
                normalized = self.normalize_header(alias)
                if normalized in headers:
                    indices[key] = headers.index(normalized)
                    break
            else:
                self.finished.emit(f"Coluna '{key}' não encontrada!")
                return

        start_row = header_row[0].row + 1
        for row in sheet.iter_rows(min_row=start_row, values_only=True):
            if not any(row[:4]):
                continue

            try:
                duracao = row[indices["duracao"]]
                duracao_min = self.convert_duration(duracao)
                valor = row[indices["preco"]]

                output_row = [
                    row[indices["data"]],
                    row[indices["origem"]],
                    row[indices["servico"]],
                    row[indices["regiao"]],
                    row[indices["destino"]],
                    duracao,
                    duracao_min,
                    float(str(valor).replace(',', '.')) if valor else 0.0
                ]
                output_sheet.append(output_row)

            except Exception as e:
                self.finished.emit(f"Erro na linha: {str(e)[:50]}")

    def equalize_regiao(self, sheet):
        """Equalização da coluna Região"""
        for row in sheet.iter_rows(min_row=2):  # Pula cabeçalho
            cell = row[self.COLUNA_REGIAO]
            if not cell.value:
                continue
                
            valor = str(cell.value).lower()
            if "fixo" in valor:
                cell.value = "Fixo"
            elif any(x in valor for x in ["movel", "móvel"]):
                cell.value = "Movel"
            elif valor.strip() == "":
                cell.value = "Intragrupo"

    def define_styles(self, wb):
        """Configura todos os estilos necessários"""
        # Estilo para minutos decimais
        self.minutes_style.number_format = '0.0'
        
        # Estilos existentes
        self.general_style.number_format = 'General'
        self.date_style.number_format = 'hh:mm:ss'
        self.accounting_style.number_format = 'R$ #,##0.00'

        wb.add_named_style(self.general_style)
        wb.add_named_style(self.date_style)
        wb.add_named_style(self.accounting_style)
        wb.add_named_style(self.minutes_style)