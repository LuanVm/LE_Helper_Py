import os
import shutil
from PyQt6.QtCore import QThread, pyqtSignal

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