import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QLabel, QComboBox, QMessageBox,
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, QSize, QEvent, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QIcon, QEnterEvent

# Business/Logic
from services.ProcessamentoAgitel import ProcessadorAgitel
from services.AutomacaoColeta import Blume

# UI/Interface
from qt_ui.homeScreen import HomeScreen
from qt_ui.IAutomacaoColeta import PainelAutomacaoColeta
from qt_ui.IMesclaPlanilhas import PainelMesclaPlanilha
from qt_ui.IOrganizacaoPastas import PainelOrganizacaoPastas
from qt_ui.IProcessamentoAgitel import PainelProcessamentoAgitel
from qt_ui.ISubstituicaoSimples import PainelSubstituicaoSimples
from qt_ui.IOrganizacaoSicoob import PainelOrganizacaoSicoob
from qt_ui.IPreenchimentoContrato import PainelPreenchimentoContrato

# Utils/Modules
from utils.windowManager import ResizableWindow
from utils.themeManager import GerenTema

### Corrigir bug dos retangulos perderem elementos no X ao redimensionar antes de trocar tema
### Adicionar tratamento de faturas vencidas na classe de automação em selenium
### Corrigir bug onde é identificado mais que 1 /span contendo "Pagar boleto", em que ele tenta acessar antes de retornar para billings

class AnimatedButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._normal_icon_size = QSize(15, 15)
        self._hover_icon_size = QSize(16, 16)
        self.setIconSize(self._normal_icon_size)
        self.anim = QPropertyAnimation(self, b"iconSize")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.setMouseTracking(True)
        #self.blume = Blume(parent=self, caminho_dados)

    def enterEvent(self, event: QEnterEvent):
        self.anim.setEndValue(self._hover_icon_size)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.setEndValue(self._normal_icon_size)
        self.anim.start()
        super().leaveEvent(event)


class MainApp(ResizableWindow):
    def __init__(self):
        super().__init__()
        self.settings_path = "config.ini"
        self._initialize_ui()
        self._setup_connections()
        self._finalize_ui_setup()
        self._title_bar = self.barra_titulo

    def _initialize_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._set_window_icon()

        self.function_groupsping = {
            "Home": 0,
            "Automação da Coleta": 1,
            "Organização de Pastas": 2,
            "Processamento Agitel": 3,
            "Mesclagem de Planilhas": 4,
            "Substituição Simples": 5,
            "Organizador (NF) Sicoob": 6,
            "Preenchimento de contrato": 7
        }

        self._configure_ui_components()
        self._setup_content_panes()
        self._setup_theme_manager()

        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.central_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        QApplication.processEvents()

    def _set_window_icon(self):
        caminho_base = Path(__file__).resolve().parent / "resources" / "icons"
        caminho_icone = caminho_base / "logo.ico"
        if caminho_icone.exists():
            self.setWindowIcon(QIcon(str(caminho_icone)))

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

        self.button_home = AnimatedButton(self.barra_titulo)
        caminho_icone = Path(__file__).resolve().parent.parent / "resources" / "ui" / "home_light.png"
        self.button_home.setIcon(QIcon(str(caminho_icone)))
        self.button_home.setFixedSize(QSize(20, 20))
        self.button_home.clicked.connect(self.mostrar_home)
        left_section.addWidget(self.button_home)

        layout_titulo.addLayout(left_section)
        layout_titulo.addStretch()
        self._add_control_buttons(layout_titulo)

        self.layout.addWidget(self.barra_titulo)

    def _add_app_icon(self, layout):
        caminho_base = Path(__file__).resolve().parent / "resources" / "icons"
        caminho_icone = caminho_base / "logo.ico"

        icone_titulo = QLabel()
        if caminho_icone.exists():
            icone_titulo.setPixmap(
                QPixmap(str(caminho_icone)).scaled(
                    24, 24,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        layout.addWidget(icone_titulo)

    def _add_control_buttons(self, layout):
        self.button_theme = AnimatedButton(self.barra_titulo)
        self.button_theme.setFixedSize(QSize(20, 20))

        self.button_minimize = AnimatedButton(self.barra_titulo)
        self.button_minimize.setFixedSize(QSize(20, 20))
        self.button_minimize.clicked.connect(self.showMinimized)

        self.button_exit = AnimatedButton(self.barra_titulo)
        self.button_exit.setFixedSize(QSize(20, 20))
        #self.button_exit.clicked.connect(self.blume.fechar_navegadores)
        self.button_exit.clicked.connect(self.close)

        layout.addWidget(self.button_theme)
        layout.addWidget(self.button_minimize)
        layout.addWidget(self.button_exit)

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
            self.organizador_sicoob,
            self.preenchimento_contrato,
            self.button_theme,
            self.button_minimize,
            self.button_exit,
            self.button_home
        )

    def _setup_content_panes(self):
        self.central_content = QWidget(self.central_widget)
        self.content_layout = QVBoxLayout(self.central_content)

        self.stacked_content = QStackedWidget(self.central_content)
        self.content_layout.addWidget(self.stacked_content)

        self.home_screen = HomeScreen()
        self.automacao_coleta = PainelAutomacaoColeta()
        self.organizacao_pastas = PainelOrganizacaoPastas()
        self.processamento_agitel = PainelProcessamentoAgitel()
        self.painel_mesclagem = PainelMesclaPlanilha()
        self.substituicao_simples = PainelSubstituicaoSimples()
        self.organizador_sicoob = PainelOrganizacaoSicoob()
        self.preenchimento_contrato = PainelPreenchimentoContrato()

        self.processamento_agitel.processStarted.connect(self._iniciar_processamento_agitel)

        self.stacked_content.addWidget(self.home_screen)
        self.stacked_content.addWidget(self.automacao_coleta)
        self.stacked_content.addWidget(self.organizacao_pastas)
        self.stacked_content.addWidget(self.processamento_agitel)
        self.stacked_content.addWidget(self.painel_mesclagem)
        self.stacked_content.addWidget(self.substituicao_simples)
        self.stacked_content.addWidget(self.organizador_sicoob)
        self.stacked_content.addWidget(self.preenchimento_contrato)

        self.layout.addWidget(self.central_content, stretch=1)

    def _iniciar_processamento_agitel(self):
        file_path = self.processamento_agitel.get_file_path()
        equalize = self.processamento_agitel.get_equalize_option()

        if not file_path:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo Excel.")
            return

        self.controller_agitel = ProcessadorAgitel(
            file_path=file_path,
            equalize=equalize
        )

        self.controller_agitel.progressUpdated.connect(self.processamento_agitel.update_progress)
        self.controller_agitel.processFinished.connect(self.processamento_agitel.on_process_finished)
        self.controller_agitel.errorOccurred.connect(self.processamento_agitel.show_error)
        self.controller_agitel.logUpdated.connect(self.processamento_agitel.append_log)

        self.controller_agitel.start()
        self.processamento_agitel.set_processing_state(True)

    def _setup_connections(self):
        self.funcionalidades_combo.currentTextChanged.connect(self.on_combo_text_changed)
        self.home_screen.boxes_clicked.connect(self.on_boxes_clicked)

    def on_combo_text_changed(self, text):
        index = self.function_groupsping.get(text, 0)
        self.stacked_content.setCurrentIndex(index)
        self._refresh_layout()

    def on_boxes_clicked(self, index):
        function_groups = {
            0: ["Automação da Coleta"],
            1: ["Organização de Pastas", "Processamento Agitel",
                "Mesclagem de Planilhas", "Substituição Simples"],
            2: ["Organizador (NF) Sicoob"],
            3: ["Preenchimento de contrato"]
        }
        self.funcionalidades_combo.clear()
        if index in function_groups:
            self.funcionalidades_combo.addItems(function_groups[index])
        else:
            self.funcionalidades_combo.addItem("Home")

    def mostrar_home(self):
        self.stacked_content.setCurrentIndex(0)
        self.funcionalidades_combo.clear()
        self.funcionalidades_combo.addItem("Home")
        self.funcionalidades_combo.setCurrentIndex(0)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.theme_manager.update_icons()
            self.theme_manager.aplicar_tema()
        super().changeEvent(event)

    def _refresh_layout(self):
        try:
            if not self.isMaximized():
                self.central_widget.updateGeometry()
                self.stacked_content.updateGeometry()
        except Exception as e:
            print(f"Erro ao atualizar layout: {e}")

    def _finalize_ui_setup(self):
        self.theme_manager.register_widget(self.automacao_coleta)
        self.theme_manager.register_widget(self.processamento_agitel)
        self.theme_manager.register_widget(self.organizacao_pastas)
        self.theme_manager.register_widget(self.painel_mesclagem)
        self.theme_manager.register_widget(self.organizador_sicoob)
        self.theme_manager.register_widget(self.preenchimento_contrato)
        self.theme_manager.register_widget(self.home_screen)
        self.theme_manager.update_icons()
        self.theme_manager.aplicar_tema()
        self.button_theme.clicked.connect(self.theme_manager.alternar_modo)

    def closeEvent(self, event):
        if hasattr(self.automacao_coleta, 'automator') and hasattr(self.automacao_coleta.automator, 'drivers'):
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