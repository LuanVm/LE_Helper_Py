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
from PainelOrganizacaoPastas import PainelOrganizacaoPastas
from GerenJanela import ResizableWindow
from GerenTema import GerenTema
from AppHome import HomeScreen

class MainApp(ResizableWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.settings_path = "config.ini"
        self.setWindowTitle("LE Helper")
        self.setGeometry(100, 100, 1200, 750)
        
        self.function_groupsping = {
            "Home": 0,
            "Automação da Coleta": 1,
            "Organização de Pastas": 2,
            "Processamento Agitel": 3,
        }
        
        self._configure_ui_components()
        self._setup_content_panes()
        self._setup_theme_manager()
        self._finalize_ui_setup()

    def _configure_ui_components(self):
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        self._setup_title_bar()

    def _setup_title_bar(self):
        self.barra_titulo = QWidget(self.central_widget)
        self.barra_titulo.setObjectName("barra_titulo")
        self.barra_titulo.setFixedHeight(30)
        
        layout_titulo = QHBoxLayout(self.barra_titulo)
        layout_titulo.setContentsMargins(5, 0, 5, 0)
        layout_titulo.setSpacing(5)
        
        left_section = QHBoxLayout()
        left_section.setContentsMargins(0, 0, 0, 0)
        left_section.setSpacing(5)
        self._add_app_icon(left_section)
        
        self.funcionalidades_combo = QComboBox(self.barra_titulo)
        self.funcionalidades_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.funcionalidades_combo.addItems([
            "Home", 
            "Automação da Coleta", 
            "Organização de Pastas",
            "Processamento Agitel"
        ])
        left_section.addWidget(self.funcionalidades_combo)
        
        self.botao_home = QPushButton(self.barra_titulo)
        self.botao_home.setIcon(QIcon(os.path.join("resources", "home_light.png")))
        self.botao_home.setFixedSize(QSize(20, 20))
        self.botao_home.clicked.connect(self.mostrar_home)
        left_section.addWidget(self.botao_home)
        
        layout_titulo.addLayout(left_section)
        layout_titulo.addStretch()
        self._add_control_buttons(layout_titulo)
        
        self.layout.addWidget(self.barra_titulo)

    def _add_app_icon(self, layout):
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
        caminho_base = os.path.join(os.path.dirname(__file__), "resources")
        
        self.botao_modo = QPushButton(self.barra_titulo)
        self.botao_modo.setIcon(QIcon(os.path.join(caminho_base, "ui_light.png")))
        self.botao_modo.setFixedSize(QSize(20, 20))
        
        self.botao_minimizar = QPushButton(self.barra_titulo)
        self.botao_minimizar.setIcon(QIcon(os.path.join(caminho_base, "ui_minimize_light.png")))
        self.botao_minimizar.setFixedSize(QSize(20, 20))
        self.botao_minimizar.clicked.connect(self.showMinimized)
        
        self.botao_fechar = QPushButton(self.barra_titulo)
        self.botao_fechar.setIcon(QIcon(os.path.join(caminho_base, "ui_exit_light.png")))
        self.botao_fechar.setFixedSize(QSize(20, 20))
        self.botao_fechar.clicked.connect(self.close)
        
        layout.addWidget(self.botao_modo)
        layout.addWidget(self.botao_minimizar)
        layout.addWidget(self.botao_fechar)

    def _setup_theme_manager(self):
        """Atualizado para incluir o novo painel"""
        self.theme_manager = GerenTema(
            self,
            self.central_widget,
            self.barra_titulo,
            self.funcionalidades_combo,
            self.automacao_coleta,
            self.organizacao_pastas,
            self.gui_processamento_agitel,
            self.botao_modo,
            self.botao_minimizar,
            self.botao_fechar,
            self.botao_home
        )

    def _setup_content_panes(self):
        self.central_content = QWidget(self.central_widget)
        self.content_layout = QVBoxLayout(self.central_content)
        
        self.stacked_content = QStackedWidget(self.central_content)
        self.content_layout.addWidget(self.stacked_content)
        
        self.home_screen = HomeScreen()
        self.automacao_coleta = InterfaceAutoBlume(self)
        self.organizacao_pastas = PainelOrganizacaoPastas(self)
        self.gui_processamento_agitel = PainelProcessamentoAgitel(self)
        
        self.stacked_content.addWidget(self.home_screen)              #Índice 0
        self.stacked_content.addWidget(self.automacao_coleta)         #Índice 1
        self.stacked_content.addWidget(self.organizacao_pastas)       #Índice 2
        self.stacked_content.addWidget(self.gui_processamento_agitel) #Índice 3
        
        
        self.funcionalidades_combo.currentTextChanged.connect(self.on_combo_text_changed)
        self.home_screen.square_clicked.connect(self.on_square_clicked)
        
        self.layout.addWidget(self.central_content, stretch=1)
    
    def on_combo_text_changed(self, text):
        index = self.function_groupsping.get(text, 0)
        self.stacked_content.setCurrentIndex(index)

    def on_square_clicked(self, index):
        function_groups = {
            0: ["Automação da Coleta"],  # Grupo Coleta
            1: ["Organização de Pastas", "Processamento Agitel"],  # Grupo Planilhamento
            2: []  # Grupo Financeiro (vazio por enquanto)
        }
        if index in function_groups:
            self.funcionalidades_combo.clear()
            if index == 1:  # Se for Planilhamento
                self.funcionalidades_combo.addItems(function_groups[index])
            else:
                self.funcionalidades_combo.addItem(function_groups[index][0] if function_groups[index] else "Home")

    def mostrar_home(self):
        """Volta para a tela inicial com todas as opções"""
        self.stacked_content.setCurrentIndex(0)
        self.funcionalidades_combo.clear()
        self.funcionalidades_combo.addItems([
            "Home", 
            "Automação da Coleta", 
            "Organização de Pastas",
            "Processamento Agitel"
        ])
        self.funcionalidades_combo.setCurrentIndex(0)

    def _finalize_ui_setup(self):
        """Atualizado para registrar o novo painel"""
        self.theme_manager.register_widget(self.automacao_coleta)
        self.theme_manager.register_widget(self.gui_processamento_agitel)
        self.theme_manager.register_widget(self.organizacao_pastas)
        self.theme_manager.update_icons()
        self.theme_manager.aplicar_tema()
        self.botao_modo.clicked.connect(self.theme_manager.alternar_modo)

    def closeEvent(self, event):
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