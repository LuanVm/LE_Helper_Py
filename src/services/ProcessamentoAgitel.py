# Lógica de Negócios - ProcessamentoAgitel.py
import re
import os
import gc
import logging
from datetime import time as dt_time, datetime as dt_datetime
from openpyxl import load_workbook, Workbook
from openpyxl.utils import datetime as xl_datetime
from openpyxl.styles import Font, Alignment, NamedStyle
from PyQt6.QtCore import QThread, pyqtSignal
import unicodedata

class ProcessamentoAgitel(QThread):
    progress_updated = pyqtSignal(int)
    process_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    log_updated = pyqtSignal(str)

    COLUNAS_SAIDA = [
        'Data', 'Origem', 'Serviço', 'Região', 
        'Destino', 'Duração', 'Duração (minutos)', 'Valor'
    ]

    def __init__(self):
        super().__init__()
        self._setup_styles()
        self._file_path = None
        self._equalize = False

    def processar(self, file_path, equalize):
        self._file_path = file_path
        self._equalize = equalize
        self.start()

    def run(self):
        try:
            wb = load_workbook(self._file_path, read_only=True)
            output_wb = Workbook()
            output_sheet = output_wb.active
            self._processar_planilhas(wb, output_sheet)
            self._finalizar_processamento(output_wb, output_sheet)
        except Exception as e:
            self._handle_error(e)
        finally:
            self._cleanup_resources(wb, output_wb)

    def _processar_planilhas(self, wb, output_sheet):
        valid_sheets = self._identificar_abas_validas(wb)
        total_sheets = len(valid_sheets)
        progress_per_sheet = 100 / total_sheets if total_sheets > 0 else 0

        self._create_header(output_sheet)

        for index, sheet in enumerate(valid_sheets, 1):
            self._processar_aba(sheet, output_sheet, index, progress_per_sheet)

    def _identificar_abas_validas(self, wb):
        valid_sheets = []
        primeira_aba = wb.worksheets[0].title.lower() if wb.worksheets else ""
        ignorar_primeira = "resumo" in primeira_aba

        for sheet in wb.worksheets:
            if ignorar_primeira and sheet == wb.worksheets[0]:
                continue
            if self._find_header_row(sheet):
                valid_sheets.append(sheet)
            else:
                self.log_updated.emit(f"Aviso: {sheet.title} ignorada (cabeçalho não encontrado)")
        return valid_sheets

    def _processar_aba(self, sheet, output_sheet, index, progress_per_sheet):
        if self.isInterruptionRequested():
            return

        # Verifica se já foi processada
        if not hasattr(sheet, '_processada'):
            self.log_updated.emit(f"Processando: {sheet.title}")
            sheet._processada = True  # Marca como processada

        header_row = self._find_header_row(sheet)
        if not header_row:
            return

        indices = self._get_column_indices(header_row)
        
        for chunk in self._process_linhas(sheet, header_row, indices):
            if self.isInterruptionRequested():
                return
            for row in chunk:
                output_sheet.append(row)

        self._atualizar_progresso(index, progress_per_sheet)

    def _process_linhas(self, sheet, header_row, indices):
        start_row = header_row[0].row + 1
        rows = list(sheet.iter_rows(min_row=start_row, values_only=True))
        chunk = []

        for row in rows:
            if self.isInterruptionRequested():
                return
            processed_row = self._process_row(row, indices)
            if processed_row:
                chunk.append(processed_row)
        yield chunk

    def _process_row(self, row, indices):
        try:
            data = self._convert_date(row[indices['data']]) or ""
            origem = str(row[indices['origem']] or "").strip()
            destino = str(row[indices['destino']] or "").strip()
            
            return [
                data,
                origem,
                str(row[indices['servico']] or ""),
                str(row[indices['regiao']] or ""),
                destino,
                self._convert_duration(row[indices['duracao']]),
                self._duration_to_minutes(row[indices['duracao']]),
                self._parse_currency(row[indices['preco']])
            ]
        except Exception as e:
            self.log_updated.emit(f"Linha ignorada: {str(e)[:50]}")
            return None

    def _finalizar_processamento(self, output_wb, output_sheet):
        self._clean_and_sort_output(output_sheet)
        self._apply_final_formatting(output_sheet)
        
        if self._equalize:
            self._equalize_regiao(output_sheet)
        
        output_path = self._get_output_path()
        output_wb.save(output_path)
        self.process_finished.emit(f"Arquivo salvo em: {output_path}")

    def _clean_and_sort_output(self, sheet):
        """Remove linhas vazias e classifica por Região com verificação de limite"""
        try:
            max_rows = 1048576  # Limite máximo do Excel
            
            # Coletar linhas válidas
            all_rows = []
            for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                if row_idx > max_rows:
                    self.log_updated.emit("Aviso: Limite de linhas do Excel atingido. Dados truncados.")
                    break
                    
                if any(cell not in (None, "", 0) for cell in row):
                    all_rows.append(row)

            # Verificar se ultrapassou o limite após coleta
            if len(all_rows) + 1 > max_rows:  # +1 para o cabeçalho
                self.log_updated.emit("Erro: Os dados excedem o limite máximo de linhas do Excel.")
                raise ValueError("Limite de linhas do Excel excedido")

            # Ordenar e reinserir
            all_rows.sort(key=lambda x: str(x[3]).lower() if x[3] else "")
            
            # Limpar dados existentes (de forma segura)
            if sheet.max_row > 1:
                sheet.delete_rows(2, sheet.max_row)
                
            # Adicionar linhas respeitando o limite
            for row in all_rows[:max_rows-1]:  # -1 para o cabeçalho
                sheet.append(row)

        except Exception as e:
            self.log_updated.emit(f"Erro na organização: {str(e)[:50]}")
            raise

    def _apply_final_formatting(self, sheet):
        for row in sheet.iter_rows(min_row=2):
            cell = row[5]
            cell.number_format = 'hh:mm:ss'

    def _setup_styles(self):
        self.styles = {
            'date': NamedStyle(name="date", number_format='YYYY-MM-DD HH:MM:SS'),
            'minutes': NamedStyle(name="minutes", number_format='0.0'),
            'currency': NamedStyle(name="currency", number_format='R$ #,##0.00'),
            'duration': NamedStyle(name="duration", number_format='hh:mm:ss')
        }

    def _create_header(self, sheet):
        sheet.append(self.COLUNAS_SAIDA)
        for col, title in enumerate(self.COLUNAS_SAIDA, 1):
            cell = sheet.cell(row=1, column=col)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        sheet.column_dimensions['F'].number_format = 'hh:mm:ss'

    def _get_output_path(self):
        base, _ = os.path.splitext(self._file_path)
        return f"{base}_leitura_agitel.xlsx"

    def _convert_date(self, value):
        if isinstance(value, dt_datetime):
            return xl_datetime.to_excel(value)
        return value

    def _convert_duration(self, value):
        if isinstance(value, dt_time):
            return value.hour/24 + value.minute/1440 + value.second/86400
        elif isinstance(value, str):
            try:
                h, m, s = map(int, value.split(':'))
                return h/24 + m/1440 + s/86400
            except:
                return 0.0
        return value

    def _duration_to_minutes(self, value):
        if isinstance(value, dt_time):
            return round(value.hour * 60 + value.minute + value.second / 60, 1)
        return 0.0

    def _parse_currency(self, value):
        try:
            return float(str(value).replace('R$', '').replace(',', '.').strip())
        except:
            return 0.0

    def _equalize_regiao(self, sheet):
        for row in sheet.iter_rows(min_row=2):
            cell = row[3]
            if cell.value:
                valor = str(cell.value).lower()
                if "fixo" in valor:
                    cell.value = "Fixo"
                elif any(x in valor for x in ["movel", "móvel"]):
                    cell.value = "Móvel"
                elif not valor.strip():
                    cell.value = "Intragrupo"

    def _find_header_row(self, sheet):
        essential_columns = {'data', 'origem', 'destino', 'duracao', 'preco'}
        for row in sheet.iter_rows(max_row=20):
            found = set()
            for cell in row:
                if cell.value:
                    normalized = self._normalize(str(cell.value))
                    if normalized in essential_columns:
                        found.add(normalized)
            if found >= essential_columns:
                return row
        return None

    def _get_column_indices(self, header_row):
        headers = [self._normalize(str(cell.value)) for cell in header_row]
        mapping = {
            'data': ['data', 'datachamada', 'datahora', 'datahorario'],
            'origem': ['origem', 'ramalorigem', 'setor', 'operador'],
            'servico': ['servico', 'tiposervico', 'serviço', 'tipochamada'],
            'regiao': ['regiao', 'região', 'localchamada', 'ddd'],
            'destino': ['destino', 'numerodestino', 'telefone', 'ramaldestino'],
            'duracao': ['duracao', 'tempochamada', 'tempogasto', 'duraçao'],
            'preco': ['preco', 'custochamada', 'valor', 'tarifa']
        }
        indices = {}
        for key, aliases in mapping.items():
            for alias in aliases:
                if self._normalize(alias) in headers:
                    indices[key] = headers.index(self._normalize(alias))
                    break
            else:
                raise ValueError(f"Coluna '{key}' não encontrada")
        return indices

    def _normalize(self, text):
        return ''.join(c for c in unicodedata.normalize('NFD', str(text).lower()) 
                      if not unicodedata.combining(c))

    def _handle_error(self, error):
        error_msg = f"Erro crítico: {str(error)}"
        self.error_occurred.emit(error_msg)
        logging.exception(error_msg)

    def _cleanup_resources(self, wb, output_wb):
        if wb: wb.close()
        if output_wb: output_wb.close()
        gc.collect()

    def _atualizar_progresso(self, index, progress_per_sheet):
        current_progress = int(index * progress_per_sheet)
        self.progress_updated.emit(min(current_progress, 100))