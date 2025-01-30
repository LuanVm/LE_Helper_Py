import re
import os
import gc
import logging
import unicodedata
from datetime import time as dt_time, datetime as dt_datetime
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment, NamedStyle
from openpyxl.utils import datetime as xl_datetime
from PyQt6.QtCore import QThread, pyqtSignal

class ProcessadorAgitel(QThread):
    progressUpdated = pyqtSignal(int)
    processFinished = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)
    logUpdated = pyqtSignal(str)

    COLUNAS_SAIDA = [
        'Data', 'Origem', 'Serviço', 'Região', 
        'Destino', 'Duração', 'Duração (minutos)', 'Valor'
    ]

    def __init__(self, file_path, equalize):
        super().__init__()
        self.file_path = file_path
        self.equalize = equalize
        self._interrupted = False
        self._setup_styles()

    def _setup_styles(self):
        self.styles = {
            'date': NamedStyle(name="date", number_format='YYYY-MM-DD HH:MM:SS'),
            'minutes': NamedStyle(name="minutes", number_format='0.0'),
            'currency': NamedStyle(name="currency", number_format='R$ #,##0.00'),
            'duration': NamedStyle(name="duration", number_format='hh:mm:ss')
        }

    def run(self):
        try:
            wb = load_workbook(self.file_path, read_only=True)
            valid_sheets = []
            batch_counter = 0

            primeira_aba = wb.worksheets[0].title.lower() if wb.worksheets else ""
            ignorar_primeira = "resumo" in primeira_aba

            for sheet in wb.worksheets:
                if self._interrupted:
                    break
                if ignorar_primeira and sheet == wb.worksheets[0]:
                    continue
                    
                if self._find_header_row(sheet):
                    valid_sheets.append(sheet)
                else:
                    self.logUpdated.emit(f"Aviso: {sheet.title} ignorada (cabeçalho não encontrado)")

            total_sheets = len(valid_sheets)
            progress_per_sheet = 100 / total_sheets if total_sheets > 0 else 0

            output_wb = Workbook()
            output_sheet = output_wb.active
            self._create_header(output_wb, output_sheet)

            for index, sheet in enumerate(valid_sheets, 1):
                if self._interrupted:
                    break

                self.logUpdated.emit(f"Processando: {sheet.title}")
                
                for chunk in self._process_sheet(sheet):
                    for row in chunk:
                        output_sheet.append(row)

                self.progressUpdated.emit(int(index * progress_per_sheet))

                batch_counter += 1
                if batch_counter >= 10 or index == total_sheets:
                    self._clean_and_sort_output(output_sheet)
                    batch_counter = 0

            self._apply_final_formatting(output_sheet)
            if self.equalize:
                self._equalize_regiao(output_sheet)

            output_path = self._get_output_path()
            output_wb.save(output_path)
            self.processFinished.emit(f"Arquivo salvo em: {output_path}")

        except Exception as e:
            self.errorOccurred.emit(f"Erro crítico: {str(e)}")
            logging.exception("Erro durante o processamento")
        finally:
            if 'wb' in locals(): wb.close()
            if 'output_wb' in locals(): output_wb.close()
            gc.collect()

    def _clean_and_sort_output(self, sheet):
        try:
            all_rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if any(cell not in (None, "", 0) for cell in row):
                    all_rows.append(row)

            all_rows.sort(key=lambda x: str(x[3]).lower() if x[3] else "")

            sheet.delete_rows(2, sheet.max_row)
            for row in all_rows:
                sheet.append(row)

        except Exception as e:
            self.logUpdated.emit(f"Erro na organização: {str(e)[:50]}")

    def _apply_final_formatting(self, sheet):
        for row in sheet.iter_rows(min_row=2):
            cell = row[5]
            cell.number_format = 'hh:mm:ss'

    def _process_sheet(self, sheet):
        header_row = self._find_header_row(sheet)
        if not header_row:
            return

        indices = self._get_column_indices(header_row)
        start_row = header_row[0].row + 1
        chunk = []

        rows = list(sheet.iter_rows(min_row=start_row, values_only=True))
        total_rows = len(rows)
        current_index = 0

        while current_index < total_rows:
            if self._interrupted:
                return

            row = rows[current_index]
            current_index += 1

            processed_row = self._process_row(row, indices)
            if processed_row:
                chunk.append(processed_row)
        if chunk:
            yield chunk

    def _process_row(self, row, indices):
        try:
            data = self._convert_date(row[indices.get('data', -1)]) or ""
            origem = str(row[indices.get('origem', -1)] or "").strip()
            destino = str(row[indices.get('destino', -1)] or "").strip()
            
            return [
                data,
                origem,
                str(row[indices.get('servico', -1)] or ""),
                str(row[indices.get('regiao', -1)] or ""),
                destino,
                self._convert_duration(row[indices.get('duracao', -1)]),
                self._duration_to_minutes(row[indices.get('duracao', -1)]),
                self._parse_currency(row[indices.get('preco', -1)])
            ]
        except Exception as e:
            self.logUpdated.emit(f"Linha ignorada: {str(e)[:50]}")
            return None

    def _create_header(self, wb, sheet):
        sheet.append(self.COLUNAS_SAIDA)
        for col, title in enumerate(self.COLUNAS_SAIDA, 1):
            cell = sheet.cell(row=1, column=col)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        sheet.column_dimensions['F'].number_format = 'hh:mm:ss'

    def _get_output_path(self):
        base, ext = os.path.splitext(self.file_path)
        return f"{base}_leitura_agitel{ext}"

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
            if not cell.value:
                continue
                
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
            if self._is_data_row(row):
                continue
                
            found = set()
            for cell in row:
                if cell.value:
                    normalized = self._normalize(str(cell.value))
                    if normalized in essential_columns:
                        found.add(normalized)
            
            if found >= essential_columns:
                return row
        return None
    
    def _is_data_row(self, row):
        data_patterns = 0
        for cell in row:
            if isinstance(cell.value, (dt_datetime, int, float)):
                data_patterns += 1
            elif isinstance(cell.value, str):
                if re.match(r"\d{2}/\d{2}/\d{4}", cell.value):
                    data_patterns += 1
                elif re.match(r"\d{2}:\d{2}:\d{2}", cell.value):
                    data_patterns += 1
                elif "R$" in cell.value:
                    data_patterns += 1
        
        return data_patterns >= 3

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
                normalized = self._normalize(alias)
                if normalized in headers:
                    indices[key] = headers.index(normalized)
                    break
            else:
                raise ValueError(f"Coluna '{key}' não encontrada")
        return indices

    def _normalize(self, text):
        return ''.join(c for c in unicodedata.normalize('NFD', str(text).lower()) 
                      if not unicodedata.combining(c))

    def stop(self):
        self._interrupted = True