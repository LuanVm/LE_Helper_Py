import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QLabel, QComboBox,
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon

from PainelAutomacaoColeta import InterfaceAutoBlume
from PainelProcessamentoAgitel import PainelProcessamentoAgitel
from GerenJanela import ResizableWindow
from GerenTema import GerenTema
from AppHome import HomeScreen

class MainApp(ResizableWindow):
    def __init__(self):
        super().__init__()
        
        # Configurações básicas da janela
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.settings_path = "config.ini"
        self.setWindowTitle("LE Helper")
        self.setGeometry(100, 100, 1200, 750)
        
        # Configuração inicial da interface
        self._configure_ui_components()
        self._setup_content_panes()
        self._setup_theme_manager()
        self._finalize_ui_setup()

    def _configure_ui_components(self):
        """Configura componentes básicos da UI"""
        # Widget central
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Barra de título
        self._setup_title_bar()

    def _setup_title_bar(self):
        """Configura a barra de título personalizada"""
        self.barra_titulo = QWidget(self.central_widget)
        self.barra_titulo.setObjectName("barra_titulo")
        self.barra_titulo.setFixedHeight(30)
        
        layout_titulo = QHBoxLayout(self.barra_titulo)
        layout_titulo.setContentsMargins(5, 0, 5, 0)
        layout_titulo.setSpacing(5)
        
        # Seção esquerda (ícone + combo + home)
        left_section = QHBoxLayout()
        left_section.setContentsMargins(0, 0, 0, 0)
        left_section.setSpacing(5)
        self._add_app_icon(left_section)
        
        self.funcionalidades_combo = QComboBox(self.barra_titulo)
        self.funcionalidades_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.funcionalidades_combo.addItems([
            "Home", 
            "Automação coleta", 
            "Processamento Agitel"
        ])
        left_section.addWidget(self.funcionalidades_combo)
        
        # Botão Home
        self.botao_home = QPushButton(self.barra_titulo)
        self.botao_home.setIcon(QIcon(os.path.join("resources", "home_light.png")))
        self.botao_home.setFixedSize(QSize(20, 20))
        self.botao_home.clicked.connect(self.mostrar_home)
        left_section.addWidget(self.botao_home)
        
        layout_titulo.addLayout(left_section)
        
        # Stretch para empurrar os botões para a direita
        layout_titulo.addStretch()
        
        # Botões de controle
        self._add_control_buttons(layout_titulo)
        
        self.layout.addWidget(self.barra_titulo)

    def _add_app_icon(self, layout):
        """Adiciona ícone na barra de título"""
        caminho_base = os.path.join(os.path.dirname(__file__), "resources")
        caminho_icone = os.path.join(caminho_base, "logo.png")
        
        icone_titulo = QLabel()
        if os.path.exists(caminho_icone):
            icone_titulo.setPixmap(QPixmap(caminho_icone).scaled(
                24, 24, 
                Qt.AspectRatioMode.IgnoreAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
        layout.addWidget(icone_titulo)

    def _add_control_buttons(self, layout):
        """Adiciona botões de controle da janela"""
        caminho_base = os.path.join(os.path.dirname(__file__), "resources")
        
        # Botão de tema
        self.botao_modo = QPushButton(self.barra_titulo)
        self.botao_modo.setIcon(QIcon(os.path.join(caminho_base, "ui_light.png")))
        self.botao_modo.setFixedSize(QSize(20, 20))
        
        # Botão minimizar
        self.botao_minimizar = QPushButton(self.barra_titulo)
        self.botao_minimizar.setIcon(QIcon(os.path.join(caminho_base, "ui_minimize_light.png")))
        self.botao_minimizar.setFixedSize(QSize(20, 20))
        self.botao_minimizar.clicked.connect(self.showMinimized)
        
        # Botão fechar
        self.botao_fechar = QPushButton(self.barra_titulo)
        self.botao_fechar.setIcon(QIcon(os.path.join(caminho_base, "ui_exit_light.png")))
        self.botao_fechar.setFixedSize(QSize(20, 20))
        self.botao_fechar.clicked.connect(self.close)
        
        layout.addWidget(self.botao_modo)
        layout.addWidget(self.botao_minimizar)
        layout.addWidget(self.botao_fechar)

    def _setup_theme_manager(self):
        """Configura o gerenciador de temas"""
        self.theme_manager = GerenTema(
            self,
            self.central_widget,
            self.barra_titulo,
            self.funcionalidades_combo,
            self.automacao_coleta,
            self.gui_processamento_agitel,
            self.botao_modo,
            self.botao_minimizar,
            self.botao_fechar,
            self.botao_home
        )

    def _setup_content_panes(self):
        """Configura os painéis de conteúdo"""
        # Área de conteúdo dinâmico
        self.central_content = QWidget(self.central_widget)
        self.content_layout = QVBoxLayout(self.central_content)
        
        # Criar QStackedWidget primeiro
        self.stacked_content = QStackedWidget(self.central_content)
        self.content_layout.addWidget(self.stacked_content)
        
        # Criação dos painéis
        self.home_screen = HomeScreen()
        self.automacao_coleta = InterfaceAutoBlume(self)
        self.gui_processamento_agitel = PainelProcessamentoAgitel(self)
        
        # Adição ao layout NA ORDEM CORRETA
        self.stacked_content.addWidget(self.home_screen)
        self.stacked_content.addWidget(self.automacao_coleta)
        self.stacked_content.addWidget(self.gui_processamento_agitel)
        
        # Conexão dos sinais
        self.funcionalidades_combo.currentIndexChanged.connect(
        lambda index: self.stacked_content.setCurrentIndex(index)
        )
        self.home_screen.square_clicked.connect(self.on_square_clicked)
        
        self.layout.addWidget(self.central_content, stretch=1)
    
    def on_square_clicked(self, index):
        ###### Index 0 = Primeiro quadrado (Automação) -> Stacked 1 / Combo 1
        ###### Index 1 = Segundo quadrado (Planilhamento) -> Stacked 2 / Combo 2
        self.stacked_content.setCurrentIndex(index + 1)
        self.funcionalidades_combo.setCurrentIndex(index + 1)

    def mostrar_home(self):
        """Volta para a tela inicial"""
        self.stacked_content.setCurrentIndex(0)
        self.funcionalidades_combo.setCurrentIndex(0)

    def _finalize_ui_setup(self):
        """Finaliza a configuração da UI"""
        # Registro de componentes
        self.theme_manager.register_widget(self.automacao_coleta)
        self.theme_manager.register_widget(self.gui_processamento_agitel)
        
        # Atualização de temas
        self.theme_manager.update_icons()
        self.theme_manager.aplicar_tema()
        
        # Conexões finais
        self.botao_modo.clicked.connect(self.theme_manager.alternar_modo)

    def closeEvent(self, event):
        """Lida com o fechamento seguro do app"""
        if hasattr(self.automacao_coleta, 'automator'):
            if hasattr(self.automacao_coleta.automator, 'drivers'):
                for driver in self.automacao_coleta.automator.drivers:
                    try:
                        driver.quit()
                    except Exception as e:
                        print(f"Erro ao fechar navegador: {e}")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())