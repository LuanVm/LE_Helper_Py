import re
import sys
import os
import time
import pandas as pd
import shutil

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QComboBox,
    QWidget, QGridLayout, QMessageBox, QTextEdit, QSizePolicy, QFileDialog, QLineEdit, QVBoxLayout
)
from PyQt6.QtCore import QThreadPool, QRunnable, pyqtSlot, QSettings, Qt
from PyQt6.QtGui import QIcon, QTextCursor
from openpyxl import load_workbook
from PyPDF2 import PdfReader
from utils.Input import HoverButton, estilo_input

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QLabel {
                font-family: 'Open Sans';
                font-size: 12px;
                color: white;
            }
            QGroupBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 20px;
            }
            QGroupBox:title {
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            """)

        # Load Excel data
        self.data_path = "resources/coleta.xlsx"
        self.df = pd.read_excel(self.data_path)
        self.df = self.df[self.df['STATUS'] != 'COLETADO IA']
        self.df = self.df.sort_values(by='VENCIMENTO', ascending=True)

        # Set up the UI
        self.setWindowTitle("LE - Automacao de Coleta")
        self.setWindowIcon(QIcon("resources/logo.ico"))
        self.setGeometry(100, 100, 800, 450)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()  # Usando QVBoxLayout para a disposição principal
        self.central_widget.setLayout(self.layout)

        # Initialize the save_directory and other settings
        self.settings = QSettings("LE - Automacao de Coleta", "Settings")
        self.save_directory = self.settings.value("save_directory", "")

        # Initialize the UI
        self.init_ui()

        # Thread pool
        self.threadpool = QThreadPool()

    def init_ui(self):
        # Layout para a linha de campos de salvamento e botoes
        top_layout = QGridLayout()

        # Diretorio de Salvamento
        self.save_dir_field = QLineEdit(self)
        self.save_dir_field.setReadOnly(True)
        self.save_dir_field.setText(self.save_directory)
        top_layout.addWidget(QLabel("Local de Salvamento:"), 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)  # Alinhando o rotulo
        top_layout.addWidget(self.save_dir_field, 0, 1)
        self.save_dir_button = HoverButton("Selecionar Pasta", self)
        self.save_dir_button.clicked.connect(self.select_save_directory)
        top_layout.addWidget(self.save_dir_button, 0, 2)  # Colocando o botao na mesma linha

        # Operadora selection
        self.operadora_combo = QComboBox(self)
        operadoras = self.df['OPERADORA'].dropna().unique()
        self.operadora_combo.addItems(operadoras)
        top_layout.addWidget(QLabel("Selecionar Operadora:"), 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)  # Alinhando o rotulo
        top_layout.addWidget(self.operadora_combo, 1, 1)

        self.confirm_button = HoverButton("Iniciar automação", self)
        self.confirm_button.clicked.connect(self.start_automation)

        top_layout.addWidget(self.confirm_button, 1, 2)  # Colocando o botao na mesma linha

        # Adicionando a linha ao layout principal
        self.layout.addLayout(top_layout)

        # Layout para os logs
        logs_layout = QGridLayout()

        # Log tecnico (primeiro log ocupa colunas 0 a 1)
        self.log_tecnico_label = QLabel("Log Técnico:", self)
        logs_layout.addWidget(self.log_tecnico_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        self.log_tecnico_area = QTextEdit(self)
        self.log_tecnico_area.setReadOnly(True)
        logs_layout.addWidget(self.log_tecnico_area, 1, 0, 1, 2)  # Ocupa duas colunas

        # Faturas coletadas (segundo log ocupa colunas 2 a 3)
        self.faturas_coletadas_label = QLabel("Faturas Coletadas:", self)
        logs_layout.addWidget(self.faturas_coletadas_label, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        self.faturas_coletadas_area = QTextEdit(self)
        self.faturas_coletadas_area.setReadOnly(True)
        logs_layout.addWidget(self.faturas_coletadas_area, 1, 2, 1, 2)  # Ocupa duas colunas

        # Ajustando espaco entre elementos
        logs_layout.setVerticalSpacing(10)  # Aumentando o espaco vertical para mais clareza
        logs_layout.setHorizontalSpacing(10)  # Aumentando o espaco horizontal para melhor distribuicao

        # Garantindo que os textos fiquem mais proximos
        logs_layout.setColumnStretch(0, 2)  # Ajustando as colunas para melhor visualizacao
        logs_layout.setColumnStretch(1, 3)
        logs_layout.setColumnStretch(2, 2)
        logs_layout.setColumnStretch(3, 3)

        # Adicionando a area de logs ao layout principal
        self.layout.addLayout(logs_layout)

        # Ajuste das proporcoes das colunas e linhas no grid para garantir redimensionamento
        top_layout.setColumnStretch(0, 1)  # Ajustando a coluna de rotulos
        top_layout.setColumnStretch(1, 4)  # Ajustando a coluna de inputs
        top_layout.setColumnStretch(2, 1)  # Ajustando a coluna do botao

        logs_layout.setRowStretch(0, 1)  # Ajustando a altura da primeira linha de logs
        logs_layout.setRowStretch(1, 4)  # Ajustando a altura da segunda linha de logs

        # Ajuste do redimensionamento dos elementos (campo, lista e botao)
        self.save_dir_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)  # Campo de diretorio expande
        self.operadora_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)  # Combo de operadora expande
        self.confirm_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)  # Botao de iniciar expande
        self.save_dir_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)  # Botao de selecionar pasta expande
        self.log_tecnico_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Log tecnico expande
        self.faturas_coletadas_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Faturas coletadas expande

    def select_save_directory(self):
        """Permite selecionar o diretório de salvamento e atualiza o estado do botão."""
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Diretório de Salvamento")
        if dir_path:
            self.save_directory = dir_path
            self.settings.setValue("save_directory", dir_path)
            QMessageBox.information(self, "Diretório Selecionado", f"Diretório de salvamento selecionado: {dir_path}")
        else:
            self.save_directory = ""

    def log_message(self, message, area="tecnico"):
        """Adiciona mensagens ao log da interface."""
        if area == "tecnico":
            self.log_tecnico_area.append(message)
            cursor = self.log_tecnico_area.textCursor()  # Obtem o cursor atual do widget de texto
            cursor.movePosition(QTextCursor.MoveOperation.End)  # Corrigido: uso do MoveOperation.End
            self.log_tecnico_area.setTextCursor(cursor)  # Aplica o cursor de volta no widget
        elif area == "faturas":
            self.faturas_coletadas_area.append(message)
            cursor = self.faturas_coletadas_area.textCursor()  # Obtem o cursor atual do widget de texto
            cursor.movePosition(QTextCursor.MoveOperation.End)  # Corrigido: uso do MoveOperation.End
            self.faturas_coletadas_area.setTextCursor(cursor)  # Aplica o cursor de volta no widget

    def start_automation(self):
        """Inicia o processo de automacao baseado na operadora selecionada."""
        selected_operadora = self.operadora_combo.currentText()

        if not self.save_directory:
            QMessageBox.warning(self, "Erro", "Selecione um diretório de salvamento primeiro.")
            return

        if not selected_operadora:
            QMessageBox.warning(self, "Erro", "Selecione uma operadora.")
            return

        user_data = self.df[self.df['OPERADORA'] == selected_operadora]
        if user_data.empty:
            QMessageBox.warning(self, "Erro", f"Nenhum dado encontrado para a operadora {selected_operadora}.")
            return

        if selected_operadora.upper() == "BLUME":
            automator = Blume(self, self.df)
        else:
            QMessageBox.warning(self, "Erro", f"Automação para a operadora {selected_operadora} nao esta implementada.")
            return

        task = AutomationTask(automator, user_data, self.log_message)
        self.threadpool.start(task)

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
            return driver
        except Exception as e:
            self.parent.log_message(f"Erro ao iniciar o navegador: {type(e).__name__} - {e}")
            raise

    def run_automation(self, user_data):
        self.parent.log_message("Iniciando processo de automação para a operadora Blume...", area="tecnico")

        for _, user in user_data.iterrows():
            if user['STATUS'] == 'COLETADO IA':
                self.parent.log_message(f"Estrutura {user['LOGIN']} ja coletada, ignorando...", area="tecnico")
                continue

            driver = None
            try:
                driver = self.initialize_browser()
                wait = WebDriverWait(driver, 15)

                driver.get("https://portal.blumetelecom.com.br")
                time.sleep(2)
                self.parent.log_message("Pagina de login carregada, iniciando login...", area="tecnico")
                self.login(driver, wait, user)

                self.parent.log_message("Login bem-sucedido, iniciando processamento dos boletos...", area="tecnico")
                self.process_boletos(driver, wait, user)

            except Exception as e:
                self.parent.log_message(f"Erro durante o processamento do usuario {user['LOGIN']}: {str(e)}", area="tecnico")
            finally:
                if driver:
                    self.parent.log_message("Fechando o navegador...", area="tecnico")
                    driver.quit()

            remaining_status = self.df[self.df['STATUS'].isnull()]
            if remaining_status.empty:
                self.parent.log_message(f"Coleta finalizada para o login {user['LOGIN']}.", area="tecnico")
            else:
                self.parent.log_message(
                    f"Ainda existem {len(remaining_status)} boletos para coletar no login {user['LOGIN']}.", area="tecnico"
                )

        remaining_data = self.df[self.df['STATUS'] != 'COLETADO IA']
        if remaining_data.empty:
            self.parent.log_message("Todos os dados foram processados e coletados.", area="tecnico")
        else:
            self.parent.log_message(f"Ainda existem {len(remaining_data)} estruturas a serem processadas.", area="tecnico")

    def login(self, driver, wait, user_data):
        try:
            self.parent.log_message("Tentando acessar a página de login...")

            email_field = wait.until(EC.presence_of_element_located((By.ID, "loginUsername")))
            password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            login_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "MuiButton-label")))
            time.sleep(1)

            self.parent.log_message("Campos de login encontrados, preenchendo informações...")

            if email_field.is_displayed() and email_field.is_enabled():
                email_field.clear()
                email = user_data['LOGIN']
                email_field.send_keys(email)
            else:
                raise Exception("Campo de e-mail não está interativo.")

            if password_field.is_displayed() and password_field.is_enabled():
                password_field.clear()
                password = user_data['SENHA']
                password_field.send_keys(password)
            else:
                raise Exception("Campo de senha não está interativo.")
            try:
                time.sleep(1)
                if login_button.is_displayed() and login_button.is_enabled():
                    login_button.click()
                else:
                    raise Exception("Botão de login não está interativo.")
            except Exception as e:
                self.parent.log_message(f"Erro ao clicar no botão de login: {e}")
                self.parent.log_message("Tentando forçar o clique via JavaScript...")
                driver.execute_script("arguments[0].click();", login_button)

            time.sleep(2)

            driver.get("https://portal.blumetelecom.com.br/billings")
            wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Pagar boleto']")))

            self.parent.log_message("Login realizado com sucesso.")

        except Exception as e:
            self.parent.log_message(f"Erro durante o login: {e}")
            raise

    def download_boleto(self, wait, user_data, index):
        """Realiza o download do boleto e processa as informações do PDF."""
        try:
            download_button = wait.until(
                EC.presence_of_element_located((By.XPATH, "//p[text()='Baixar boleto']"))
            )
            if not download_button.is_enabled():
                self.parent.log_message("Botão de download não está habilitado.")
                return

            download_button.click()
            self.parent.log_message("Iniciando o download do boleto...")
            self.wait_for_download()
            download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            latest_file = self.get_latest_file(download_dir)

            if latest_file:
                self.parent.log_message(f"Boleto baixado: {latest_file}")
                contrato = self.extrair_contrato_pdf(latest_file)
                self.handle_downloaded_file(contrato, latest_file, user_data)
            else:
                self.parent.log_message(f"Erro ao baixar o boleto {index}: Arquivo não encontrado.")

        except Exception as e:
            self.parent.log_message(f"Erro ao processar o download do boleto {index}: {str(e)}")

    def handle_downloaded_file(self, contrato, latest_file):
        """Manipula o arquivo baixado."""
        if contrato:
            # Certifique-se de que o contrato é uma string sem zeros à esquerda
            contrato = str(contrato).lstrip('0').strip()
            self.parent.log_message(f"Número do contrato extraído: {contrato}")

            # Certifique-se de que todos os dados na coluna IDENTIFICAÇÃO são strings sem zeros à esquerda
            self.parent.df['IDENTIFICAÇÃO'] = self.parent.df['IDENTIFICAÇÃO'].astype(str).str.lstrip('0').str.strip()

            if contrato in self.parent.df['IDENTIFICAÇÃO'].values:
                row = self.parent.df[self.parent.df['IDENTIFICAÇÃO'] == contrato].iloc[0]
                nomenclatura = row['NOMENCLATURA']
                destino = os.path.join(self.parent.save_directory, f"{nomenclatura}.pdf")
                shutil.move(latest_file, destino)
                self.parent.log_message(f"Arquivo renomeado para: {destino}")
                self.parent.df.loc[self.parent.df['IDENTIFICAÇÃO'] == contrato, 'STATUS'] = 'COLETADO IA'
                self.parent.df.to_excel(self.parent.data_path, index=False)
            else:
                self.parent.log_message(f"Contrato {contrato} não encontrado na planilha.")
                self.mover_boleto_nao_encontrado(latest_file)
        else:
            self.parent.log_message(f"Contrato não extraído do PDF: {latest_file}")
            self.mover_boleto_nao_encontrado(latest_file)
    
    def process_boletos(self, driver, wait, user_data):
        try:
            processed_boleto_ids = set()

            while True:
                self.parent.log_message("Acessando página de billings...")
                driver.get("https://portal.blumetelecom.com.br/billings")
                time.sleep(2)

                # Atualiza os elementos antes de iterar novamente
                boleto_buttons = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//span[text()='Pagar boleto']"))
                )
                boletos_disponiveis = [
                    button for idx, button in enumerate(boleto_buttons)
                    if f"button-{idx}" not in processed_boleto_ids
                ]
                self.parent.log_message(f"Botões 'Pagar boleto' encontrados: {len(boleto_buttons)}")

                for index, button in enumerate(boleto_buttons):
                    try:
                        boleto_id = f"button-{index}"
                        if boleto_id in processed_boleto_ids:
                            self.parent.log_message(f"Boleto {boleto_id} já processado, ignorando...")
                            continue

                        self.parent.log_message(f"Preparando para processar 'Pagar boleto - {index + 1}'...")
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)

                        try:
                            button.click()
                        except Exception as click_exception:
                            self.parent.log_message(f"Erro ao clicar no botão: {click_exception}")
                            self.parent.log_message("Tentando forçar o clique via JavaScript...")
                            driver.execute_script("arguments[0].click();", button)

                        processed_boleto_ids.add(boleto_id)

                        # Baixar boleto
                        self.download_boleto(driver, wait, user_data, index + 1)

                        self.parent.log_message("Voltando para a página de billings após processar o boleto...")
                        driver.get("https://portal.blumetelecom.com.br/")
                        time.sleep(1)
                        driver.get("https://portal.blumetelecom.com.br/billings")
                        
                    except Exception as e:
                        self.parent.log_message(f"Erro ao processar botão {index + 1}: {e}")

                # Atualiza a lista de botões e filtra os não processados
                boleto_buttons = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//span[text()='Pagar boleto']"))
                )
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

    def wait_for_download(self):
        """Espera até que o download seja concluído."""
        download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        timeout = 60
        while timeout > 0:
            pdf_files = [fname for fname in os.listdir(download_dir) if fname.endswith(".pdf")]
            if pdf_files:
                # Aguarda alguns segundos adicionais para garantir que o arquivo esteja completamente gravado
                time.sleep(2)
                return
            time.sleep(1)
            timeout -= 1
        raise Exception("Tempo de download excedido.")

    def extrair_contrato_pdf(self):
        """Extrai o número do contrato de um arquivo PDF."""
        try:
            leitor = PdfReader(self.pdf_path)
            texto = ""
            for pagina in leitor.pages:
                texto += pagina.extract_text()

            # Regex para encontrar o contrato
            padrao = r'\b0{3,}\d+\b'
            match = re.search(padrao, texto)
            return match.group(0) if match else None
        except Exception as e:
            self.parent.log_message(f"Erro ao processar o PDF {self.pdf_path}: {str(e)}")
            return None
        
    def mover_boleto_nao_encontrado(self, pdf_path):
        """Move boletos não encontrados para a pasta 'Boleto não encontrado'."""
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

    def comparar_e_atualizar_excel(self, contrato, pdf_path, nomenclatura):
        """Compara o contrato com a coluna IDENTIFICAÇÃO e atualiza o STATUS."""
        try:
            contrato = contrato.lstrip('0').strip()
            self.parent.df['IDENTIFICAÇÃO'] = self.parent.df['IDENTIFICAÇÃO'].astype(str).str.lstrip('0').str.strip()

            if contrato in self.parent.df['IDENTIFICAÇÃO'].values:
                row = self.parent.df[self.parent.df['IDENTIFICAÇÃO'] == contrato].iloc[0]
                nomenclatura = row['NOMENCLATURA']
                destino = os.path.join(self.parent.save_directory, f"{nomenclatura}.pdf")
                shutil.move(pdf_path, destino)
                self.parent.log_message(f"Arquivo renomeado para: {destino}")
                self.parent.df.loc[self.parent.df['IDENTIFICAÇÃO'] == contrato, 'STATUS'] = 'COLETADO IA'
                self.parent.df.to_excel(self.parent.data_path, index=False)
                return True
            else:
                self.parent.log_message(f"Contrato {contrato} não encontrado na planilha.")
                return False
        except Exception as e:
            self.parent.log_message(f"Erro ao comparar e atualizar Excel: {str(e)}")
            return False

    def get_latest_file(self, directory):
        """Retorna o arquivo mais recente no diretório."""
        try:
            files = [os.path.join(directory, fname) for fname in os.listdir(directory) if fname.endswith('.pdf')]
            return max(files, key=os.path.getmtime) if files else None
        except Exception as e:
            self.parent.log_message(f"Erro ao obter o arquivo mais recente: {str(e)}")
            return None

    def mark_as_collected(self, excel_identification, data_path):
        """Marca o boleto como coletado no Excel."""
        try:
            self.parent.df['IDENTIFICAÇÃO'] = self.parent.df['IDENTIFICAÇÃO'].astype(str).str.lstrip('0').str.strip()
            if excel_identification in self.parent.df['IDENTIFICAÇÃO'].values:
                self.parent.df.loc[self.parent.df['IDENTIFICAÇÃO'] == excel_identification, 'STATUS'] = 'COLETADO IA'
                self.parent.df.to_excel(data_path, index=False)
                self.parent.log_message(f"Status atualizado para 'COLETADO IA' para {excel_identification}")
            else:
                self.parent.log_message(f"Identificação {excel_identification} não encontrada.")
        except Exception as e:
            self.parent.log_message(f"Erro ao marcar como coletado: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())
