import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QLabel, QComboBox, QGraphicsOpacityEffect,
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt, QSettings, QSize, QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtGui import QIcon, QPixmap

#Automação Blume
from GuiAutoBlume import GuiAutoBlume
from AutoBlume import StopAutomation

#Estilos e gerenciamento
from GerenJanela import ResizableWindow
from GerenEstilos import (
    estilo_sheet_light, estilo_label_light, estilo_combo_box_light,
    campo_qline_light, estilo_log_light, estilo_sheet_dark, estilo_label_dark, estilo_combo_box_dark,
    campo_qline_dark, estilo_log_dark
)


class MainApp(ResizableWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(estilo_sheet_light())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.settings_path = "config.ini"
        self.modo_escuro = False
        self.setWindowTitle("LE Helper")
        self.setGeometry(100, 100, 1100, 650)
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setStyleSheet(estilo_sheet_light())
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.barra_titulo = QWidget(self.central_widget)
        self.barra_titulo.setObjectName("barra_titulo")
        self.barra_titulo.setFixedHeight(30)
        layout_titulo = QHBoxLayout(self.barra_titulo)
        layout_titulo.setContentsMargins(5, 0, 5, 0)
        layout_titulo.setSpacing(5)
        
        # Define the base path for resources
        caminho_base = os.path.join(os.path.dirname(__file__), "resources")
        
        icone_titulo = QLabel()
        caminho_icone = os.path.join(caminho_base, "logo.png")
        if os.path.exists(caminho_icone):
            icone_titulo.setPixmap(QPixmap(caminho_icone).scaled(24, 24, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            print(f"Icon not found: {caminho_icone}")
        layout_titulo.addWidget(icone_titulo)
        
        self.funcionalidades_combo = QComboBox(self.barra_titulo)
        self.funcionalidades_combo.addItem("Automação coleta")
        self.funcionalidades_combo.setStyleSheet(estilo_combo_box_light())
        self.funcionalidades_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.funcionalidades_combo.currentTextChanged.connect(self.mudar_funcionalidade)
        layout_titulo.addWidget(self.funcionalidades_combo)
        layout_titulo.addStretch()
        
        # Use the base path for all icons
        self.botao_modo = QPushButton(self.barra_titulo)
        self.botao_modo.setObjectName("botao_modo")
        icon_path = os.path.join(caminho_base, "ui_light.png")
        if os.path.exists(icon_path):
            self.botao_modo.setIcon(QIcon(icon_path))
        else:
            print(f"Icon not found: {icon_path}")
        self.botao_modo.setFixedSize(QSize(20, 20))
        self.botao_modo.setStyleSheet("background-color: transparent; border: none;")
        self.botao_modo.clicked.connect(self.alternar_modo)
        layout_titulo.addWidget(self.botao_modo)
        
        self.botao_minimizar = QPushButton(self.barra_titulo)
        self.botao_minimizar.setObjectName("botao_minimizar")
        icon_minimize = os.path.join(caminho_base, "ui_minimize_light.png")
        if os.path.exists(icon_minimize):
            self.botao_minimizar.setIcon(QIcon(icon_minimize))
        else:
            print(f"Icon not found: {icon_minimize}")
        self.botao_minimizar.setFixedSize(QSize(20, 20))
        self.botao_minimizar.setStyleSheet("background-color: transparent; border: none;")
        self.botao_minimizar.clicked.connect(self.showMinimized)
        layout_titulo.addWidget(self.botao_minimizar)
        
        self.botao_fechar = QPushButton(self.barra_titulo)
        self.botao_fechar.setObjectName("botao_fechar")
        icon_exit = os.path.join(caminho_base, "ui_exit_light.png")
        if os.path.exists(icon_exit):
            self.botao_fechar.setIcon(QIcon(icon_exit))
        else:
            print(f"Icon not found: {icon_exit}")
        self.botao_fechar.setFixedSize(QSize(20, 20))
        self.botao_fechar.setStyleSheet("background-color: transparent; border: none;")
        self.botao_fechar.clicked.connect(self.close)
        layout_titulo.addWidget(self.botao_fechar)
        
        self.layout.addWidget(self.barra_titulo)
        self.central_content = QWidget(self.central_widget)
        self.layout.addWidget(self.central_content)
        self.content_layout = QVBoxLayout(self.central_content)
        self.gui_auto_blume = GuiAutoBlume(self)
        self.content_layout.addWidget(self.gui_auto_blume)
        self.load_settings()
        if self.modo_escuro:
            self.aplicar_estilo_dark()
        else:
            self.aplicar_estilo_light()

    def closeEvent(self, event):
        if hasattr(self.gui_auto_blume, 'automator'):
            stop_automation = StopAutomation(self.gui_auto_blume.automator)
            stop_automation.stop()
            if hasattr(self.gui_auto_blume.automator, 'drivers'):
                for driver in self.gui_auto_blume.automator.drivers:
                    try:
                        driver.quit()
                    except Exception as e:
                        print(f"Erro ao fechar o navegador: {e}")
        event.accept()

    def load_settings(self):
        settings = QSettings(self.settings_path, QSettings.Format.IniFormat)
        self.modo_escuro = settings.value("dark_mode", False, type=bool)

    def save_settings(self):
        settings = QSettings(self.settings_path, QSettings.Format.IniFormat)
        settings.setValue("dark_mode", self.modo_escuro)

    def alternar_modo(self):
        if self.modo_escuro:
            self.aplicar_estilo_light()
        else:
            self.aplicar_estilo_dark()
        self.modo_escuro = not self.modo_escuro
        self.botao_modo.setIcon(QIcon("resources/ui_dark.png" if self.modo_escuro else "resources/ui_light.png"))
        self.botao_minimizar.setIcon(QIcon("resources/ui_minimize_dark.png" if self.modo_escuro else "resources/ui_minimize_light.png"))
        self.botao_fechar.setIcon(QIcon("resources/ui_exit_dark.png" if self.modo_escuro else "resources/ui_exit_light.png"))
        self.animar_fade()

    def animar_fade(self):
        opacity_effect = QGraphicsOpacityEffect(self.central_widget)
        self.central_widget.setGraphicsEffect(opacity_effect)
        animacao = QPropertyAnimation(opacity_effect, b"opacity")
        animacao.setDuration(300)
        animacao.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animacao.setStartValue(1.0)
        animacao.setEndValue(0.5)
        animacao_reversa = QPropertyAnimation(opacity_effect, b"opacity")
        animacao_reversa.setDuration(300)
        animacao_reversa.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animacao_reversa.setStartValue(0.5)
        animacao_reversa.setEndValue(1.0)
        animacao_reversa.finished.connect(lambda: self.central_widget.setGraphicsEffect(None))
        animacao.finished.connect(animacao_reversa.start)
        animacao.start()

    def aplicar_estilo_light(self):
        self.setStyleSheet(estilo_sheet_light())
        self.central_widget.setStyleSheet(estilo_sheet_light())
        self.barra_titulo.setStyleSheet(estilo_sheet_light())
        self.funcionalidades_combo.setStyleSheet(estilo_combo_box_light())
        self.gui_auto_blume.setStyleSheet(estilo_sheet_light())
        self.gui_auto_blume.save_dir_field.setPlaceholderText('Selecione o diretório de salvamento...')
        self.gui_auto_blume.save_dir_field.setStyleSheet(campo_qline_light())
        self.gui_auto_blume.planilha_field.setPlaceholderText('Selecione a planilha de dados...')
        self.gui_auto_blume.planilha_field.setStyleSheet(campo_qline_light())
        self.gui_auto_blume.operadora_combo.setStyleSheet(estilo_combo_box_light())
        self.gui_auto_blume.log_tecnico_area.setStyleSheet(estilo_log_light())
        self.gui_auto_blume.faturas_coletadas_area.setStyleSheet(estilo_log_light())
        self.gui_auto_blume.label_salvamento.setStyleSheet(estilo_label_light())
        self.gui_auto_blume.label_planilha.setStyleSheet(estilo_label_light())
        self.gui_auto_blume.label_operadora.setStyleSheet(estilo_label_light())
        self.botao_modo.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 5px;
            }
        """)
        self.botao_minimizar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 5px;
            }
        """)
        self.botao_fechar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
                border-radius: 5px;
            }
        """)

    def aplicar_estilo_dark(self):
        self.setStyleSheet(estilo_sheet_dark())
        self.central_widget.setStyleSheet(estilo_sheet_dark())
        self.barra_titulo.setStyleSheet(estilo_sheet_dark())
        self.funcionalidades_combo.setStyleSheet(estilo_combo_box_dark())
        self.gui_auto_blume.setStyleSheet(estilo_sheet_dark())
        self.gui_auto_blume.save_dir_field.setStyleSheet(campo_qline_dark())
        self.gui_auto_blume.planilha_field.setStyleSheet(campo_qline_dark())
        self.gui_auto_blume.operadora_combo.setStyleSheet(estilo_combo_box_dark())
        self.gui_auto_blume.log_tecnico_area.setStyleSheet(estilo_log_dark())
        self.gui_auto_blume.faturas_coletadas_area.setStyleSheet(estilo_log_dark())
        self.gui_auto_blume.label_salvamento.setStyleSheet(estilo_label_dark())
        self.gui_auto_blume.label_planilha.setStyleSheet(estilo_label_dark())
        self.gui_auto_blume.label_operadora.setStyleSheet(estilo_label_dark())
        self.botao_modo.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #444444;
                border-radius: 5px;
            }
        """)
        self.botao_minimizar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #444444;
                border-radius: 5px;
            }
        """)
        self.botao_fechar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
                border-radius: 5px;
            }
        """)

    def mudar_funcionalidade(self, funcionalidade):
        if funcionalidade == "Automação coleta":
            self.content_layout.addWidget(self.gui_auto_blume)
        else:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())