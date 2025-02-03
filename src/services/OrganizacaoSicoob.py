import os
import re
from PyPDF2 import PdfReader
from PyQt6.QtCore import QThread, pyqtSignal

def extract_cnpjs_from_pdf(file_path):
    """
    Extrai CNPJs de um arquivo PDF utilizando PyPDF2.
    Returns:
        list: Lista de CNPJs encontrados no PDF.
    """
    cnpjs = []
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                # Regex para capturar o padrão: 00.000.000/0000-00
                matches = re.findall(r"\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}", text)
                cnpjs.extend(matches)
    except Exception as e:
        print(f"Erro ao processar o PDF {file_path}: {e}")
    return cnpjs

class OrganizadorSicoobThread(QThread):
    progresso = pyqtSignal(int)
    mensagem = pyqtSignal(str)
    finalizado = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, diretorio, agencias, parent=None):
        """
        Args:
            diretorio (str): Caminho da pasta com os arquivos PDF.
            agencias (dict): Dicionário onde as chaves são CNPJs (no formato “00.000.000/0000-00")
                              e os valores são os novos nomes (ex.: "PA_01").
        """
        super().__init__(parent)
        self.diretorio = diretorio
        self.agencias = agencias  # Mapeamento: CNPJ -> Agência
        self.historico = []

    def run(self):
        try:
            arquivos = [f for f in os.listdir(self.diretorio)
                        if os.path.isfile(os.path.join(self.diretorio, f))
                        and f.lower().endswith('.pdf')]
            total = len(arquivos)
            if total == 0:
                self.mensagem.emit("Nenhum arquivo PDF encontrado na pasta.")
                self.finalizado.emit(False)
                return

            for i, arquivo in enumerate(arquivos):
                caminho_origem = os.path.join(self.diretorio, arquivo)
                cnpjs = extract_cnpjs_from_pdf(caminho_origem)
                cnpj_selecionado = None
                if len(cnpjs) >= 2:
                    cnpj_selecionado = cnpjs[1]
                elif len(cnpjs) == 1:
                    cnpj_selecionado = cnpjs[0]

                if not cnpj_selecionado:
                    self.mensagem.emit(f"Arquivo '{arquivo}': Nenhum CNPJ encontrado.")
                else:
                    if cnpj_selecionado in self.agencias:
                        novo_nome_base = self.agencias[cnpj_selecionado]
                        novo_nome = novo_nome_base + ".pdf"
                        novo_caminho = os.path.join(self.diretorio, novo_nome)
                        novo_caminho = self.gerar_nome_unico(novo_caminho)
                        os.rename(caminho_origem, novo_caminho)
                        self.mensagem.emit(f"Arquivo '{arquivo}' renomeado para '{os.path.basename(novo_caminho)}'.")
                        self.historico.append((novo_caminho, caminho_origem))
                    else:
                        self.mensagem.emit(f"Arquivo '{arquivo}': CNPJ {cnpj_selecionado} não mapeado.")
                self.progresso.emit(int(((i+1) / total) * 100))
            self.finalizado.emit(True)
        except Exception as e:
            self.error.emit(f"Erro na organização: {str(e)}")
            self.finalizado.emit(False)

    def gerar_nome_unico(self, caminho):
        base, ext = os.path.splitext(caminho)
        contador = 1
        novo_caminho = caminho
        while os.path.exists(novo_caminho):
            novo_caminho = f"{base}_{contador}{ext}"
            contador += 1
        return novo_caminho
