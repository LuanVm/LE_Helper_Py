import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QLabel, QComboBox, QMessageBox,
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon

# Business/Logic
from services.SubstituicaoSimples import PainelSubstituicaoSimples
from services.ProcessamentoAgitel import ProcessadorAgitel

# UI/Interface
from qt_ui.HomeScreen import HomeScreen
from qt_ui.IAutomacaoColeta import PainelAutomacaoColeta
from qt_ui.IMesclaPlanilhas import PainelMesclaPlanilha
from qt_ui.IOrganizacaoPastas import PainelOrganizacaoPastas
from qt_ui.IProcessamentoAgitel import PainelProcessamentoAgitel

# Utils/Modules
from utils.GerenJanela import ResizableWindow
from utils.GerenTema import GerenTema

class MainApp(ResizableWindow):
    def __init__(self):
        super().__init__()
        self.settings_path = "config.ini"
        self._initialize_ui()
        self._setup_connections()
        self._finalize_ui_setup()

    def _initialize_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setWindowTitle("LE Helper")
        self.setGeometry(100, 100, 1200, 750)
        self._set_window_icon()
        
        self.function_groupsping = {
            "Home": 0,
            "Automação da Coleta": 1,
            "Organização de Pastas": 2,
            "Processamento Agitel": 3,
            "Mesclagem de Planilhas": 4,
            "Substituição Simples": 5
        }
        
        self._configure_ui_components()
        self._setup_content_panes()
        self._setup_theme_manager()

        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.central_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        QApplication.processEvents()

    def _set_window_icon(self):
        caminho_base = Path(__file__).resolve().parent.parent / "resources" / "icons"
        caminho_icone = caminho_base / "logo.ico"
        if caminho_icone.exists():
            self.setWindowIcon(QIcon(str(caminho_icone)))

    def _setup_connections(self):
        self.funcionalidades_combo.currentTextChanged.connect(self.on_combo_text_changed)
        self.home_screen.square_clicked.connect(self.on_square_clicked)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_layout()
        
        if hasattr(self, 'theme_manager') and self.theme_manager is not None:
            self.theme_manager._force_layout_update()
            self.resize(self.size() + QSize(1, 1))
            self.resize(self.size() - QSize(1, 1))
        else:
            QTimer.singleShot(100, lambda: self.resize(self.size() + QSize(1, 1)))
            QTimer.singleShot(150, lambda: self.resize(self.size() - QSize(1, 1)))

    def _refresh_layout(self):
        self.central_widget.updateGeometry()
        self.stacked_content.updateGeometry()
        for i in range(self.stacked_content.count()):
            if widget := self.stacked_content.widget(i):
                widget.updateGeometry()
        QApplication.processEvents()

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
        self.funcionalidades_combo.setFixedWidth(200)
        self.funcionalidades_combo.addItems(["Home"])
        left_section.addWidget(self.funcionalidades_combo)
        
        self.botao_home = QPushButton(self.barra_titulo)
        self.botao_home.setIcon(QIcon(os.path.join("resources","icons", "home_light.png")))
        self.botao_home.setFixedSize(QSize(20, 20))
        self.botao_home.clicked.connect(self.mostrar_home)
        left_section.addWidget(self.botao_home)
        
        layout_titulo.addLayout(left_section)
        layout_titulo.addStretch()
        self._add_control_buttons(layout_titulo)
        
        self.layout.addWidget(self.barra_titulo)

    def _add_app_icon(self, layout):
        caminho_base = Path(__file__).resolve().parent.parent / "resources" / "icons"
        caminho_icone = caminho_base / "logo.ico"
        
        icone_titulo = QLabel()
        if caminho_icone.exists():
            icone_titulo.setPixmap(QPixmap(str(caminho_icone)).scaled(
                24, 24, 
                Qt.AspectRatioMode.IgnoreAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
        layout.addWidget(icone_titulo)

    def _add_control_buttons(self, layout):
        caminho_base = Path(__file__).resolve().parent.parent / "resources" / "icons"
        
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
        self.theme_manager = GerenTema(
            self,
            self.central_widget,
            self.barra_titulo,
            self.funcionalidades_combo,
            self.automacao_coleta,
            self.organizacao_pastas,
            self.processamento_agitel,
            self.substituicao_simples,
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
        
        # Inicializa os painéis de interface
        self.home_screen = HomeScreen()
        self.automacao_coleta = PainelAutomacaoColeta()
        self.organizacao_pastas = PainelOrganizacaoPastas()
        self.processamento_agitel = PainelProcessamentoAgitel()
        self.painel_mesclagem = PainelMesclaPlanilha()
        self.substituicao_simples = PainelSubstituicaoSimples()

        # Configura conexões do processamento Agitel
        self.processamento_agitel.processStarted.connect(self._iniciar_processamento_agitel)

        # Adiciona ao stacked widget
        self.stacked_content.addWidget(self.home_screen)
        self.stacked_content.addWidget(self.automacao_coleta)
        self.stacked_content.addWidget(self.organizacao_pastas)
        self.stacked_content.addWidget(self.processamento_agitel)
        self.stacked_content.addWidget(self.painel_mesclagem)
        self.stacked_content.addWidget(self.substituicao_simples)

        self.layout.addWidget(self.central_content, stretch=1)

    def _iniciar_processamento_agitel(self):
        """Inicia o processamento quando solicitado pelo painel"""
        file_path = self.processamento_agitel.get_file_path()
        equalize = self.processamento_agitel.get_equalize_option()
        
        if not file_path:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo Excel.")
            return
        
        # Cria o controlador com os parâmetros corretos
        self.controller_agitel = ProcessadorAgitel(
            file_path=file_path,
            equalize=equalize
        )
        
        # Conecta os sinais
        self.controller_agitel.progressUpdated.connect(self.processamento_agitel.update_progress)
        self.controller_agitel.processFinished.connect(self.processamento_agitel.on_process_finished)
        self.controller_agitel.errorOccurred.connect(self.processamento_agitel.show_error)
        self.controller_agitel.logUpdated.connect(self.processamento_agitel.append_log)
        
        # Inicia o processamento
        self.controller_agitel.start()
        self.processamento_agitel.set_processing_state(True)

    def on_combo_text_changed(self, text):
        index = self.function_groupsping.get(text, 0)
        self.stacked_content.setCurrentIndex(index)
        self._refresh_layout()

    def on_square_clicked(self, index):
        function_groups = {
            0: ["Automação da Coleta"],
            1: ["Organização de Pastas", "Processamento Agitel", 
                "Mesclagem de Planilhas", "Substituição Simples"],
            2: ["Organização de notas Sicoob"]
        }

        if index in function_groups:
            self.funcionalidades_combo.clear()
            if index == 1:
                self.funcionalidades_combo.addItems(function_groups[index])
            else:
                self.funcionalidades_combo.addItem(function_groups[index][0] if function_groups[index] else "Home")

    def mostrar_home(self):
        self.stacked_content.setCurrentIndex(0)
        self.funcionalidades_combo.clear()
        self.funcionalidades_combo.addItems(["Home"])
        self.funcionalidades_combo.setCurrentIndex(0)

    def _finalize_ui_setup(self):
        self.theme_manager.register_widget(self.automacao_coleta)
        self.theme_manager.register_widget(self.processamento_agitel)
        self.theme_manager.register_widget(self.organizacao_pastas)
        self.theme_manager.register_widget(self.painel_mesclagem)
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