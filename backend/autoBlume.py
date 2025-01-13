import os
import time
import shutil
import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PyQt6.QtCore import QRunnable, pyqtSlot
from PyPDF2 import PdfReader
from openpyxl import load_workbook

class AutomationTask(QRunnable):
    def __init__(self, automator, user_data, log_function):
        super().__init__()
        self.automator = automator
        self.user_data = user_data
        self.log_function = log_function

    @pyqtSlot()
    def run(self):
        try:
            self.log_function("Iniciando automação para o usuário...")
            self.automator.run_automation(self.user_data)
            self.log_function("Automação concluída com sucesso.")
        except Exception as e:
            self.log_function(f"Erro durante a automação: {str(e)}")

class Blume:
    def __init__(self, parent, df):
        self.parent = parent
        self.df = df

    def initialize_browser(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-popup-blocking")

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            self.parent.log_message("Navegador inicializado com sucesso.")
            return driver
        except Exception as e:
            self.parent.log_message(f"Erro ao iniciar o navegador: {type(e).__name__} - {e}")
            raise

    def run_automation(self, user_data):
        self.parent.log_message("Iniciando processo de automação para a operadora Blume...", area="tecnico")

        if self.verificar_coleta_finalizada():
            self.parent.log_message("Nenhuma coleta pendente. Finalizando execução.")
            return

        for _, user in user_data.iterrows():
            if user['STATUS'] == 'COLETADO IA' or user['STATUS'] == 'INDISPONIVEL':
                self.parent.log_message(f"Estrutura {user['LOGIN']} já processada ou indisponível, ignorando...", area="tecnico")
                continue

            driver = None
            try:
                driver = self.initialize_browser()
                wait = WebDriverWait(driver, 15)
                driver.get("https://portal.blumetelecom.com.br")
                time.sleep(2)
                self.parent.log_message("Página de login carregada, iniciando login...", area="tecnico")
                self.login(driver, wait, user)

                time.sleep(2)
                driver.get("https://portal.blumetelecom.com.br/billings")

                self.parent.log_message("Login bem-sucedido, iniciando processamento dos boletos...", area="tecnico")
                self.process_boletos(driver, wait, user)

            except Exception as e:
                self.parent.log_message(f"Erro durante o processamento do usuário {user['LOGIN']}: {str(e)}", area="tecnico")
            finally:
                if driver:
                    self.parent.log_message("Fechando o navegador...", area="tecnico")
                    driver.quit()

        remaining_status = self.df[self.df['STATUS'].isnull()]
        if remaining_status.empty:
            self.parent.log_message("Todos os boletos foram processados.", area="tecnico")

    def login(self, driver, wait, user_data):
        try:
            self.parent.log_message("Tentando acessar a página de login...")

            time.sleep(1)
            email_field = wait.until(EC.presence_of_element_located((By.ID, "loginUsername")))
            password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            login_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "MuiButton-label")))

            self.parent.log_message("Campos de login encontrados, preenchendo informações...")

            email_field.clear()
            email_field.send_keys(user_data['LOGIN'])

            password_field.clear()
            password_field.send_keys(user_data['SENHA'])

            login_button.click()

            self.parent.log_message("Login realizado com sucesso.")

        except Exception as e:
            self.parent.log_message(f"Erro durante o login: {e}")
            raise

    def process_boletos(self, driver, wait, user_data):
        try:
            processed_boleto_ids = set()

            while True:
                self.parent.log_message("Acessando página de billings...")
                driver.get("https://portal.blumetelecom.com.br/billings")
                time.sleep(2)

                # Verifica a presença do texto "Você não possui faturas em aberto"
                try:
                    no_invoices_message = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//h5[contains(text(), 'Você não possui faturas em aberto')]"))
                    )
                    self.parent.log_message("Mensagem 'Você não possui faturas em aberto' encontrada.")
                    # Atualiza o status para 'INDISPONIVEL'
                    self.df.loc[self.df['LOGIN'] == user_data['LOGIN'], 'STATUS'] = 'INDISPONIVEL'
                    self.df.to_excel(self.parent.data_path, index=False)
                    self.parent.log_message("Status atualizado para 'INDISPONIVEL' na planilha.")
                    break
                except Exception:
                    # Caso não encontre a mensagem, prossegue com a coleta de boletos
                    pass

                # Captura os botões 'Pagar boleto'
                boleto_buttons = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//span[text()='Pagar boleto']"))
                )
                self.parent.log_message(f"Botões 'Pagar boleto' encontrados: {len(boleto_buttons)}")

                for index, button in enumerate(boleto_buttons):
                    boleto_id = f"button-{index}"
                    if boleto_id in processed_boleto_ids:
                        continue

                    self.parent.log_message(f"Preparando para processar 'Pagar boleto - {index + 1}'...")
                    
                    # Certifique-se de que o botão é clicável
                    try:
                        wait.until(EC.element_to_be_clickable(button))
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        button.click()
                    except Exception as e:
                        self.parent.log_message(f"Erro ao clicar no botão 'Pagar boleto - {index + 1}': {e}")
                        continue

                    processed_boleto_ids.add(boleto_id)

                    # Aguarda o redirecionamento para a página de detalhes do boleto
                    try:
                        wait.until(EC.url_contains("billings"))
                        self.download_boleto(wait, user_data, index + 1)
                        time.sleep(2)
                    except Exception as e:
                        self.parent.log_message(f"Erro após clicar em 'Pagar boleto - {index + 1}': {e}")
                        continue

                # Verifica se ainda há boletos não processados
                boletos_disponiveis = [
                    button for idx, button in enumerate(boleto_buttons)
                    if f"button-{idx}" not in processed_boleto_ids
                ]
                if not boletos_disponiveis:
                    self.parent.log_message("Todos os boletos processados ou nenhum novo encontrado.")
                    break

        except Exception as e:
            self.parent.log_message(f"Erro geral ao processar boletos: {e}")
            raise

    def download_boleto(self, wait, user_data, index):
        try:
            download_button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//p[text()='Baixar boleto']"))
            )
            download_button.click()

            self.parent.log_message("Aguardando conclusão do download...")
            self.wait_for_download()

            download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            latest_file = self.get_latest_file(download_dir)

            if latest_file:
                self.parent.log_message(f"Boleto baixado: {latest_file}", area="tecnico")
                contrato = self.extrair_contrato_pdf(latest_file)
                if contrato:  # Validar antes de continuar
                    self.handle_downloaded_file(contrato, latest_file, user_data)
            else:
                self.parent.log_message(f"Erro ao baixar o boleto {index}: Arquivo não encontrado.")

        except Exception as e:
            self.parent.log_message(f"Erro ao processar o download do boleto {index}: {e}")

    def wait_for_download(self):
        download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        timeout = 60
        while timeout > 0:
            pdf_files = [fname for fname in os.listdir(download_dir) if fname.endswith(".pdf")]
            if pdf_files:
                latest_file = os.path.join(download_dir, max(pdf_files, key=lambda f: os.path.getmtime(os.path.join(download_dir, f))))
                if not latest_file.endswith(".crdownload") and os.path.getsize(latest_file) > 0:
                    time.sleep(2)
                    return
            time.sleep(1)
            timeout -= 1
        raise Exception("Tempo de download excedido ou arquivo incompleto.")

    def extrair_contrato_pdf(self, pdf_path):
        try:
            if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
                self.parent.log_message(f"Arquivo PDF inválido: {pdf_path}")
                return None
            leitor = PdfReader(pdf_path)
            texto = ""
            for pagina in leitor.pages:
                texto += pagina.extract_text()

            # Regex ajustado para capturar especificamente o contrato no formato correto
            padrao = r'\b0{3,}(\d{3,})\b'
            match = re.search(padrao, texto)

            if match:
                contrato = match.group(1)  # Pega o grupo capturado sem os zeros à esquerda
                return contrato
            else:
                return None
        except Exception as e:
            self.parent.log_message(f"Erro ao processar o PDF {pdf_path}: {str(e)}")
            return None

    def get_latest_file(self, directory):
        try:
            files = [os.path.join(directory, fname) for fname in os.listdir(directory) if fname.endswith('.pdf')]
            return max(files, key=os.path.getmtime) if files else None
        except Exception as e:
            self.parent.log_message(f"Erro ao obter o arquivo mais recente: {e}")
            return None

    def handle_downloaded_file(self, contrato, latest_file, user_data):
        if contrato:
            contrato = contrato.lstrip('0')
            self.parent.log_message(f"Número do contrato extraído: {contrato}")

            # Normaliza os dados da coluna 'IDENTIFICAÇÃO'
            self.df['IDENTIFICAÇÃO'] = self.df['IDENTIFICAÇÃO'].astype(str).str.lstrip('0').str.strip()

            if contrato in self.df['IDENTIFICAÇÃO'].values:
                row = self.df[self.df['IDENTIFICAÇÃO'] == contrato].iloc[0]
                nomenclatura = row['NOMENCLATURA']
                destino = os.path.join(self.parent.save_directory, f"{nomenclatura}.pdf")
                
                shutil.move(latest_file, destino)
                self.parent.log_message(f"{nomenclatura}", area="faturas")

                self.df.loc[self.df['IDENTIFICAÇÃO'] == contrato, 'STATUS'] = 'COLETADO IA'

                # Preservar formatação existente
                with pd.ExcelWriter(self.parent.data_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                    self.df.to_excel(writer, index=False, startrow=1, header=False)
            else:
                self.parent.log_message(f"Contrato {contrato} não encontrado na planilha.")
                self.mover_boleto_nao_encontrado(latest_file)
        else:
            self.parent.log_message(f"Contrato não extraído do PDF: {latest_file}")
            self.mover_boleto_nao_encontrado(latest_file)

    def mover_boleto_nao_encontrado(self, pdf_path):
        output_dir = os.path.join(self.parent.save_directory, "Boleto não encontrado")
        os.makedirs(output_dir, exist_ok=True)

        base_filename = "Boleto_nao_encontrado"
        file_index = 1
        new_filename = f"{base_filename}.pdf"
        while os.path.exists(os.path.join(output_dir, new_filename)):
            new_filename = f"{base_filename}_{file_index}.pdf"
            file_index += 1

        destino = os.path.join(output_dir, new_filename)
        shutil.move(pdf_path, destino)
        self.parent.log_message(f"Boleto movido para 'Boleto não encontrado' como: {destino}")

    def comparar_e_atualizar_excel(self, contrato, pdf_path):
        try:
            contrato = contrato.lstrip('0').strip()
            self.df['IDENTIFICAÇÃO'] = self.df['IDENTIFICAÇÃO'].astype(str).str.lstrip('0').str.strip()

            if contrato in self.df['IDENTIFICAÇÃO'].values:
                row = self.df[self.df['IDENTIFICAÇÃO'] == contrato].iloc[0]
                nomenclatura = row['NOMENCLATURA']
                destino = os.path.join(self.parent.save_directory, f"{nomenclatura}.pdf")
                shutil.move(pdf_path, destino)
                self.parent.log_message(f"{nomenclatura}", area="faturas")
                self.df.loc[self.df['IDENTIFICAÇÃO'] == contrato, 'STATUS'] = 'COLETADO IA'
                self.df.to_excel(self.parent.data_path, index=False)
                return True
            else:
                self.parent.log_message(f"Contrato {contrato} não encontrado na planilha.")
                return False
        except Exception as e:
            self.parent.log_message(f"Erro ao comparar e atualizar Excel: {e}")
            return False

    def mark_as_collected(self, excel_identification, data_path):
        try:
            # Carregar o arquivo mantendo formatação
            workbook = load_workbook(data_path, keep_vba=True)
            sheet = workbook.active

            found = False
            for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, values_only=False):
                
                cell_identification = row['IDENTIFICAÇÃO'] 
                cell_status = row['STATUS']

                if cell_identification.value and str(cell_identification.value).lstrip("0").strip() == excel_identification:
                    cell_status.value = str("COLETADO IA")
                    found = True
                    break

            if found:
                # Salvar preservando a formatação
                workbook.save(data_path)
                self.parent.log_message(f"Status atualizado para 'COLETADO IA' para {excel_identification}")
            else:
                self.parent.log_message(f"Identificação {excel_identification} não encontrada.")
        except Exception as e:
            self.parent.log_message(f"Erro ao marcar como coletado: {e}")

    def verificar_coleta_finalizada(self):
        try:
            registros_nao_coletados = self.df[self.df['STATUS'] != 'COLETADO IA']

            if registros_nao_coletados.empty:
                self.parent.log_message("Todos os registros já foram coletados. Nenhuma ação necessária.")
                return True
            else:
                self.parent.log_message(f"Ainda existem {len(registros_nao_coletados)} registros para coleta.")
                return False
        except Exception as e:
            self.parent.log_message(f"Erro ao verificar a coleta: {e}")
            return False
