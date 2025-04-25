import os
import time
import shutil
import re
from openpyxl import load_workbook
from PyQt6.QtCore import QRunnable, QMutex
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PyPDF2 import PdfReader

class TarefaAutomacao(QRunnable):
    """Classe que executa a automação em uma thread separada"""
    
    def __init__(self, automator, dados_usuario, funcao_log):
        super().__init__()
        self.automator = automator
        self.dados_usuario = dados_usuario
        self.funcao_log = funcao_log

    def run(self):
        """Método principal que inicia o processo de automação"""
        try:
            self.funcao_log("Iniciando automação...", area="tecnico")
            if hasattr(self.automator, 'flag_parar') and self.automator.flag_parar:
                self.funcao_log("Automação cancelada antes de iniciar", area="tecnico")
                return
            
            self.automator.executar_automacao(self.dados_usuario)
            self.funcao_log("Automação concluída!", area="tecnico")
            
        except Exception as erro:
            self.funcao_log(f"Erro durante a automação: {str(erro)}", area="tecnico")

class PararAutomacao:
    """Classe responsável por interromper a automação em execução"""
    
    def __init__(self, automator):
        self.automator = automator

    def parar(self):
        """Para a automação e fecha todos os navegadores"""
        if hasattr(self.automator, 'flag_parar'):
            self.automator.flag_parar = True
            self.automator.parent.log_mensagem("Parando automação...", area="tecnico", cor="red")
            self.fechar_navegadores()
        else:
            self.automator.parent.log_mensagem("Nenhuma automação em execução", area="tecnico")

    def fechar_navegadores(self):
        """Fecha todas as instâncias do navegador abertas"""
        if hasattr(self.automator, 'drivers') and self.automator.drivers:
            self.automator.parent.log_mensagem("Fechando navegadores...", area="tecnico")
            for driver in self.automator.drivers:
                try:
                    driver.quit()
                except Exception as erro:
                    self.automator.parent.log_mensagem(f"Erro ao fechar navegador: {erro}", area="tecnico")
            self.automator.drivers.clear()

class Blume:
    """Classe principal que implementa a automação para a operadora Blume"""
    
    def __init__(self, parent, caminho_dados):
        self.parent = parent
        self.caminho_dados = caminho_dados
        # Ao carregar a planilha com data_only=True, obtemos os valores já calculados
        self.planilha = load_workbook(caminho_dados, data_only=True).active
        self.mutex = QMutex()
        self.flag_parar = False
        self.drivers = []

    def inicializar_navegador(self):
        """Configura e inicia uma nova instância do navegador Chrome"""
        try:
            opcoes = webdriver.ChromeOptions()
            opcoes.add_argument("--disable-extensions")
            opcoes.add_argument("--disable-popup-blocking")
            #opcoes.add_argument("--headless")
            self.parent.log_mensagem("Abrindo navegador...", area="tecnico")
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=opcoes
            )
            self.drivers.append(driver)
            return driver
        except Exception as erro:
            self.parent.log_mensagem(f"Falha ao iniciar navegador: {erro}", area="tecnico")
            raise

    def executar_automacao(self, dados_usuario):
        """Fluxo principal de execução da automação"""
        self.parent.log_mensagem("Iniciando coleta para Blume...", area="tecnico")

        if self.verificar_coleta_completa():
            self.parent.log_mensagem("Todas faturas já foram coletadas!", area="tecnico")
            return

        for usuario in dados_usuario:
            if self.flag_parar:
                self.parent.log_mensagem("Processo interrompido!", area="tecnico")
                self.fechar_navegadores()
                return

            # Se o STATUS já estiver como "COLETADO IA" ou "INDISPONIVEL", pula a execução.
            if usuario['STATUS'] in ['COLETADO IA', 'INDISPONIVEL']:
                continue

            driver = None
            try:
                driver = self.inicializar_navegador()
                wait = WebDriverWait(driver, 2)
                driver.get("https://portal.blumetelecom.com.br")
                self.fazer_login(driver, wait, usuario)
                self.processar_boletos(driver, wait, usuario)
                # Após processar boletos, marca os boletos pendentes do login como INDISPONIVEL
                self.marcar_pendentes_indisponiveis(usuario['LOGIN'])
            except Exception as erro:
                self.parent.log_mensagem(f"Erro no processamento: {str(erro)}", area="tecnico")
            finally:
                if driver:
                    driver.quit()
                    if driver in self.drivers:
                        self.drivers.remove(driver)

    def fazer_login(self, driver, wait, dados_usuario):
        """Realiza o login no portal da Blume"""
        try:
            self.parent.log_mensagem(f"Realizando login no acesso: {dados_usuario['LOGIN']}", area="tecnico")
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            campo_email = wait.until(EC.presence_of_element_located((By.ID, "loginUsername")))
            driver.execute_script("arguments[0].scrollIntoView(true);", campo_email)
            campo_email.send_keys(dados_usuario['LOGIN'])
            campo_senha = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
            driver.execute_script("arguments[0].scrollIntoView(true);", campo_senha)
            campo_senha.clear()
            campo_senha.send_keys(dados_usuario['SENHA'])
            time.sleep(1)
            botao_login = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "MuiButton-label")))
            driver.execute_script("arguments[0].scrollIntoView(true);", botao_login)
            botao_login.click()
            time.sleep(2)
            driver.get("https://portal.blumetelecom.com.br/billings")
            self.parent.log_mensagem("Login realizado com sucesso!", area="tecnico")
        except Exception as erro:
            self.parent.log_mensagem(f"Falha no login: {erro}", area="tecnico")
            raise

    def processar_boletos(self, driver, wait, dados_usuario):
        """
        Processa os boletos disponíveis no portal.
        Ao entrar na página de billings, identifica quantos textos "Pagar boleto" existem,
        numera-os (ex.: Pagar boleto - 01, Pagar boleto - 02, etc.) e processa cada um sequencialmente.
        """
        try:
            ids_processados = set()
            while True:
                driver.get("https://portal.blumetelecom.com.br/billings")
                # Verifica se há mensagem informando que não há faturas em aberto.
                try:
                    wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//h5[contains(text(), 'Você não possui faturas em aberto')]")
                        )
                    )
                    self.parent.log_mensagem("Nenhuma fatura disponível", area="tecnico")
                    # Atualiza o status do login para INDISPONIVEL para evitar reprocessamento.
                    self.atualizar_status_planilha(dados_usuario['LOGIN'], 'INDISPONIVEL')
                    return
                except:
                    pass

                try:
                    botoes_boleto = wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, "//span[text()='Pagar boleto']"))
                    )
                except Exception as erro:
                    self.parent.log_mensagem(f"Erro ao buscar boletos: {erro}", area="tecnico")
                    break

                # Registra quantos "Pagar boleto" foram encontrados
                total_botoes = len(botoes_boleto)
                self.parent.log_mensagem(f"Foram encontrados {total_botoes} boleto(s) para processar", area="tecnico")
                
                for indice, botao in enumerate(botoes_boleto):
                    id_boleto = f"botao-{indice}"
                    if id_boleto in ids_processados:
                        continue

                    # Loga qual botão está sendo processado (ex.: Pagar boleto - 01)
                    self.parent.log_mensagem(f"Processando Pagar boleto - {indice + 1}", area="tecnico")
                    try:
                        # Clique via JavaScript para agilizar a interação
                        driver.execute_script("arguments[0].click();", botao)
                        self.baixar_boleto(wait, dados_usuario, indice + 1)
                        ids_processados.add(id_boleto)
                        # Aguarda de forma dinâmica a finalização do download
                        WebDriverWait(driver, 10).until(
                            lambda d: not any(
                                f.lower().endswith(".crdownload")
                                for f in os.listdir(os.path.join(os.path.expanduser('~'), 'Downloads'))
                            )
                        )
                        # Após processar o boleto, retorna para a página de billings
                        driver.get("https://portal.blumetelecom.com.br/billings")
                    except Exception as erro:
                        self.parent.log_mensagem(f"Erro ao processar boleto {indice + 1}: {erro}", area="tecnico")
                if len(ids_processados) >= total_botoes:
                    break
        except Exception as erro:
            self.parent.log_mensagem(f"Erro geral no processamento: {erro}", area="tecnico")
            raise

    def baixar_boleto(self, wait, dados_usuario, indice):
        """Realiza o download e processamento do boleto"""
        try:
            botao_download = wait.until(
                EC.presence_of_element_located((By.XPATH, "//p[text()='Baixar boleto']"))
            )
            botao_download.click()
            # Aguarda alguns segundos para que o download tenha tempo de iniciar
            time.sleep(3)
            caminho_download = os.path.join(os.path.expanduser('~'), 'Downloads')
            arquivo = self.aguardar_download(caminho_download)
            if arquivo:
                contrato = self.extrair_contrato_pdf(arquivo)
                if contrato:
                    self.processar_arquivo_baixado(contrato, arquivo, dados_usuario)
                else:
                    # Se o contrato (boleto) não for encontrado, move o arquivo para a pasta de boletos não encontrados.
                    self.mover_arquivo_nao_encontrado(arquivo)
        except Exception as erro:
            self.parent.log_mensagem(f"Erro no download: {erro}", area="tecnico")

    def aguardar_download(self, pasta):
        """Aguarda a conclusão do download do arquivo e retorna o caminho do arquivo mais recente."""
        def nome_valido(nome):
            return re.fullmatch(r"[A-Za-z0-9]+\.(pdf|PDF)", nome) is not None

        tempo_limite = 60
        while tempo_limite > 0:
            arquivos = [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")]
            arquivos_validos = [f for f in arquivos if nome_valido(f)]
            if arquivos_validos:
                arquivo_recente = os.path.join(
                    pasta,
                    max(arquivos_validos, key=lambda f: os.path.getmtime(os.path.join(pasta, f)))
                )
                if not arquivo_recente.lower().endswith(".crdownload"):
                    return arquivo_recente
            if arquivos and not arquivos_validos:
                arquivo_recente = os.path.join(
                    pasta,
                    max(arquivos, key=lambda f: os.path.getmtime(os.path.join(pasta, f)))
                )
                if not arquivo_recente.lower().endswith(".crdownload"):
                    return arquivo_recente
            time.sleep(1)
            tempo_limite -= 1
        return None

    def extrair_contrato_pdf(self, caminho_pdf):
        """Extrai o número do contrato de um arquivo PDF"""
        try:
            # Abre o arquivo em modo binário
            with open(caminho_pdf, "rb") as f:
                leitor = PdfReader(f)
                texto = "".join(pagina.extract_text() or "" for pagina in leitor.pages)
            
            # Padrão que procura:
            # - A palavra "Contrato"
            # - O valor da fatura no formato "R$ xx,xx"
            # - Seguido pelo número do contrato com 2 a 7 dígitos, removendo zeros à esquerda
            padrao = re.compile(
                r'Contrato\s*R\$\s*\d{1,4}(?:[.,]\d{3})*[.,]\d{2}\s*0*(\d{1,7})',
                re.IGNORECASE
            )
            match = padrao.search(texto)
            if match:
                # Converte para int para remover os zeros à esquerda e volta para str
                contrato = str(int(match.group(1)))
                return contrato
            
            return None
        except Exception as erro:
            self.parent.log_mensagem(f"Erro na leitura do PDF: {erro}", area="tecnico")
            return None

    def processar_arquivo_baixado(self, contrato, arquivo, dados_usuario):
        """Processa o arquivo baixado e atualiza a planilha"""
        contrato = contrato.lstrip('0')
        # Verifica se o contrato já foi coletado (linha já marcada como 'COLETADO IA')
        for linha in self.planilha.iter_rows(min_row=2, values_only=True):
            if str(linha[4]).lstrip('0') == contrato and linha[11] == 'COLETADO IA':
                self.parent.log_mensagem(f"O contrato {contrato} já havia sido baixado.", area="tecnico")
                os.remove(arquivo)  # Remove o arquivo duplicado
                return
        # Caso contrário, procede com o processamento normal
        if self.verificar_contrato_planilha(contrato):
            nomenclatura = self.obter_nomenclatura(contrato)
            nomenclatura = re.sub(r'[<>:"/\\|?*]', '', str(nomenclatura))
            destino = os.path.join(self.parent.pasta_salvamento, f"{nomenclatura}.pdf")
            self.parent.log_mensagem(f"Movendo arquivo para: {destino}", area="tecnico")
            shutil.move(arquivo, destino)
            self.parent.log_mensagem(nomenclatura, area="faturas")
            self.atualizar_status_planilha(contrato, 'COLETADO IA')
        else:
            self.mover_arquivo_nao_encontrado(arquivo)

    def mover_arquivo_nao_encontrado(self, arquivo):
        """Move arquivos não identificados para a pasta 'Boletos não encontrados'"""
        pasta_erro = os.path.join(self.parent.pasta_salvamento, "Boletos não encontrados")
        os.makedirs(pasta_erro, exist_ok=True)
        destino = os.path.join(pasta_erro, os.path.basename(arquivo))
        shutil.move(arquivo, destino)
        self.parent.log_mensagem(f"Arquivo movido para: {destino}", area="tecnico")

    def verificar_contrato_planilha(self, contrato):
        """Verifica se o contrato existe na planilha"""
        for linha in self.planilha.iter_rows(min_row=2, values_only=True):
            if str(linha[4]).lstrip('0') == contrato:
                return True
        return False

    def obter_nomenclatura(self, contrato):
        """Obtém a nomenclatura correta do contrato"""
        for linha in self.planilha.iter_rows(min_row=2, values_only=True):
            if str(linha[4]).lstrip('0') == contrato:
                return linha[12]
        return None

    def atualizar_status_planilha(self, identificador, status):
        """
        Atualiza o status na planilha Excel para todas as linhas que batem com o identificador.
        O identificador pode ser o LOGIN ou o número do contrato (sem zeros à esquerda).
        """
        self.mutex.lock()
        try:
            for linha in self.planilha.iter_rows(min_row=2):
                if (str(linha[8].value) == identificador or str(linha[4].value).lstrip('0') == identificador):
                    linha[11].value = status
            self.planilha.parent.save(self.caminho_dados)
        finally:
            self.mutex.unlock()

    def marcar_pendentes_indisponiveis(self, login):
        """
        Após o processamento dos boletos para o usuário, percorre as linhas da planilha
        que pertencem ao login informado e marca como "INDISPONIVEL" aquelas que ainda não foram
        atualizadas para "COLETADO IA".
        """
        self.mutex.lock()
        try:
            for linha in self.planilha.iter_rows(min_row=2, values_only=False):
                if str(linha[8].value) == login and linha[11].value not in ['COLETADO IA', 'INDISPONIVEL']:
                    linha[11].value = 'INDISPONIVEL'
            self.planilha.parent.save(self.caminho_dados)
        finally:
            self.mutex.unlock()

    def verificar_coleta_completa(self):
        """
        Verifica se todas as faturas foram coletadas.
        Considera processadas as linhas que estão com status 'COLETADO IA' ou 'INDISPONIVEL'.
        """
        for linha in self.planilha.iter_rows(min_row=2, values_only=True):
            if linha[11] not in ['COLETADO IA', 'INDISPONIVEL']:
                return False
        return True

    def fechar_navegadores(self):
        """Fecha todas as instâncias do navegador"""
        for driver in self.drivers:
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()
