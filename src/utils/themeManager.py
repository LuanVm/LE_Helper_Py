import os
from pathlib import Path
from PyQt6.QtCore import QSettings, Qt, QSize, QEvent
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from utils.sheetStyles import (
    estilo_sheet_light, estilo_combo_box_light,
    estilo_sheet_dark, estilo_combo_box_dark
)

class GerenTema:
    def __init__(self, main_window, central_widget, barra_titulo, funcionalidades_combo,
                 automacao_coleta, gui_processamento_agitel, organizacao_pastas,
                 substituicao_simples, organizador_sicoob, preenchimento_contrato,
                 botao_theme, botao_minimize, botao_fechar, botao_home):
        self.main_window = main_window
        self.central_widget = central_widget
        self.barra_titulo = barra_titulo
        self.funcionalidades_combo = funcionalidades_combo
        self.automacao_coleta = automacao_coleta
        self.gui_processamento_agitel = gui_processamento_agitel
        self.organizacao_pastas = organizacao_pastas
        self.substituicao_simples = substituicao_simples
        self.organizador_sicoob = organizador_sicoob
        self.preenchimento_contrato = preenchimento_contrato
        self.botao_theme = botao_theme
        self.botao_minimize = botao_minimize
        self.botao_fechar = botao_fechar
        self.botao_home = botao_home

        self.settings_path = main_window.settings_path
        self.widgets = []
        self._modo_escuro = False

        self.load_settings()
        self.update_icons()
        self._setup_ui_properties()
        self._force_layout_update()
        self._register_components()
        self.aplicar_tema_inicial()

    def _setup_ui_properties(self):
        self.main_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main_window.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.central_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

    def _force_layout_update(self):
        self.main_window.setUpdatesEnabled(False)
        self.central_widget.updateGeometry()
        self.main_window.updateGeometry()
        self.main_window.setUpdatesEnabled(True)
        QApplication.sendEvent(self.main_window, QEvent(QEvent.Type.LayoutRequest))
        QApplication.processEvents()

    @property
    def modo_escuro(self):
        return self._modo_escuro

    @modo_escuro.setter
    def modo_escuro(self, value):
        self._modo_escuro = value
        self.save_settings()

    def load_settings(self):
        settings = QSettings(self.settings_path, QSettings.Format.IniFormat)
        self.modo_escuro = settings.value("dark_mode", False, type=bool)

    def save_settings(self):
        settings = QSettings(self.settings_path, QSettings.Format.IniFormat)
        settings.setValue("dark_mode", self.modo_escuro)

    def aplicar_tema_inicial(self):
        if self.modo_escuro:
            self.aplicar_estilo_dark()
        else:
            self.aplicar_estilo_light()

    def register_widget(self, widget):
        """Registra widgets para aplicação de estilos e atualizações."""
        self.widgets.append(widget)
        if hasattr(widget, 'apply_styles'):
            widget.apply_styles(self.modo_escuro)

    def _register_components(self):
        components = [
            self.central_widget, self.barra_titulo, self.funcionalidades_combo,
            self.automacao_coleta, self.gui_processamento_agitel, self.organizacao_pastas,
            self.substituicao_simples, self.organizador_sicoob, self.preenchimento_contrato,
            self.botao_theme, self.botao_minimize, self.botao_fechar, self.botao_home
        ]
        for component in components:
            self.register_widget(component)

    def update_icons(self):
        base_path = str(Path(__file__).resolve().parent.parent / "resources" / "ui")
        theme_suffix = "dark" if self.modo_escuro else "light"
        self.botao_home.setIcon(QIcon(os.path.join(base_path, f"home_{theme_suffix}.png")))
        self.botao_theme.setIcon(QIcon(os.path.join(base_path, f"ui_{theme_suffix}.png")))
        self.botao_minimize.setIcon(QIcon(os.path.join(base_path, f"ui_minimize_{theme_suffix}.png")))
        self.botao_fechar.setIcon(QIcon(os.path.join(base_path, f"ui_exit_{theme_suffix}.png")))
        # Atualiza ícones de painéis que possuam método update_icons
        for panel in [self.automacao_coleta, self.gui_processamento_agitel, self.organizacao_pastas]:
            if hasattr(panel, 'update_icons'):
                panel.update_icons(theme_suffix)

    def alternar_modo(self):
        self.modo_escuro = not self.modo_escuro
        self.update_icons()
        self.aplicar_tema()
        self.save_settings()

    def aplicar_tema(self):
        if self.modo_escuro:
            self.aplicar_estilo_dark()
        else:
            self.aplicar_estilo_light()

        for widget in self.widgets:
            if hasattr(widget, 'apply_styles'):
                widget.apply_styles(self.modo_escuro)

        self._force_layout_update()
        # Força uma pequena mudança de tamanho para re-renderização
        self.main_window.resize(self.main_window.size() + QSize(1, 1))
        self.main_window.resize(self.main_window.size() - QSize(1, 1))

    def _aplicar_estilo_base(self, dark_mode):
        estilo_sheet = estilo_sheet_dark() if dark_mode else estilo_sheet_light()
        estilo_combo = estilo_combo_box_dark() if dark_mode else estilo_combo_box_light()

        self.central_widget.setStyleSheet(estilo_sheet)
        self.barra_titulo.setStyleSheet(estilo_sheet)
        self.funcionalidades_combo.setStyleSheet(estilo_combo)

        # Cores dinâmicas
        botao_hover_bg = "444444" if dark_mode else "e0e0e0"
        botao_fechar_hover_bg = "ff6b6b" if dark_mode else "ff9494"
        botao_fechar_pressed_bg = "ff4444" if dark_mode else "ff6666"

        # Estilização para botões comuns (theme, minimize, home)
        for btn in [self.botao_theme, self.botao_minimize, self.botao_home]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: #{botao_hover_bg};
                    border-radius: 5px;
                }}
            """)

        # Estilização especial para botão de fechar
        self.botao_fechar.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #{botao_fechar_hover_bg};
                border-radius: 5px;
            }}
            QPushButton:pressed {{
                background-color: #{botao_fechar_pressed_bg};
            }}
        """)

    def aplicar_estilo_light(self):
        self._aplicar_estilo_base(False)
        self._aplicar_estilo_paineis(False)

    def aplicar_estilo_dark(self):
        self._aplicar_estilo_base(True)
        self._aplicar_estilo_paineis(True)

    def _aplicar_estilo_paineis(self, dark_mode):
        for panel in [self.automacao_coleta, self.gui_processamento_agitel, 
                     self.organizacao_pastas, self.substituicao_simples,
                     self.organizador_sicoob, self.preenchimento_contrato]:
            if hasattr(panel, 'apply_styles'):
                panel.apply_styles(dark_mode)