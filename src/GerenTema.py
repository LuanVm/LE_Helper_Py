import os
from PyQt6.QtCore import QSettings, Qt, QSize, QEvent
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from GerenEstilos import (
    estilo_sheet_light, estilo_combo_box_light,
    estilo_sheet_dark, estilo_combo_box_dark
)

from PainelOrganizacaoPastas import PainelOrganizacaoPastas

class GerenTema:
    def __init__(self, main_window, central_widget, barra_titulo, funcionalidades_combo,
                 automacao_coleta, gui_processamento_agitel, organizacao_pastas,
                 botao_modo, botao_minimizar, botao_fechar, botao_home):
        self.main_window = main_window
        self.central_widget = central_widget
        self.barra_titulo = barra_titulo
        self.funcionalidades_combo = funcionalidades_combo
        self.automacao_coleta = automacao_coleta
        self.gui_processamento_agitel = gui_processamento_agitel
        self.organizacao_pastas = organizacao_pastas
        self.botao_modo = botao_modo
        self.botao_minimizar = botao_minimizar
        self.botao_fechar = botao_fechar
        self.botao_home = botao_home
        self.settings_path = main_window.settings_path
        self.widgets = []
        self._modo_escuro = False
        self.load_settings()
        self.update_icons()

        self.main_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main_window.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.central_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        # Forçar atualização inicial do layout
        self._force_layout_update()

        # Registrar componentes de forma genérica
        components = [
            central_widget, barra_titulo, funcionalidades_combo,
            automacao_coleta, gui_processamento_agitel, organizacao_pastas,
            botao_modo, botao_minimizar, botao_fechar, botao_home
        ]
        for component in components:
            self.register_widget(component)

        self.aplicar_tema_inicial()

    def _force_layout_update(self):
        """Atualiza o layout imediatamente após mudanças de tema"""
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
        """Registra widgets e aplica estilos imediatamente"""
        self.widgets.append(widget)
        if isinstance(widget, PainelOrganizacaoPastas):
            widget.apply_styles(self.modo_escuro)
        elif hasattr(widget, 'apply_styles'):
            widget.apply_styles(self.modo_escuro)

    def update_icons(self):
        base_path = os.path.join(os.path.dirname(__file__), "resources")
        theme_suffix = "dark" if self.modo_escuro else "light"
        
        # Atualizar ícones principais
        self.botao_home.setIcon(QIcon(os.path.join(base_path, f"home_{theme_suffix}.png")))
        self.botao_modo.setIcon(QIcon(os.path.join(base_path, f"ui_{theme_suffix}.png")))
        self.botao_minimizar.setIcon(QIcon(os.path.join(base_path, f"ui_minimize_{theme_suffix}.png")))
        self.botao_fechar.setIcon(QIcon(os.path.join(base_path, f"ui_exit_{theme_suffix}.png")))

        # Atualizar ícones específicos dos painéis
        for panel in [self.automacao_coleta, self.gui_processamento_agitel, self.organizacao_pastas]:
            if hasattr(panel, 'update_icons'):
                panel.update_icons(theme_suffix)

    def alternar_modo(self):
        self.modo_escuro = not self.modo_escuro
        self.update_icons()
        self.aplicar_tema()
        self.save_settings()

    def aplicar_tema(self):
        style_method = self.aplicar_estilo_dark if self.modo_escuro else self.aplicar_estilo_light
        style_method()
        
        for widget in self.widgets:
            if hasattr(widget, 'apply_styles'):
                widget.apply_styles(self.modo_escuro)
        
        # Adicionar estas linhas para atualização imediata
        self._force_layout_update()
        self.main_window.resize(self.main_window.size() + QSize(1, 1))
        self.main_window.resize(self.main_window.size() - QSize(1, 1))

    def _aplicar_estilo_base(self, dark_mode):
        # Método base para evitar duplicação de código
        estilo_sheet = estilo_sheet_dark() if dark_mode else estilo_sheet_light()
        estilo_botao = ("444444" if dark_mode else "e0e0e0", "ff6b6b")

        self.central_widget.setStyleSheet(estilo_sheet)
        self.barra_titulo.setStyleSheet(estilo_sheet)
        self.funcionalidades_combo.setStyleSheet(estilo_combo_box_dark() if dark_mode else estilo_combo_box_light())

        # Aplicar estilos genéricos nos botões
        self.botao_modo.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; border: none; }}
            QPushButton:hover {{ background-color: #{estilo_botao[0]}; border-radius: 5px; }}
        """)
        self.botao_minimizar.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; border: none; }}
            QPushButton:hover {{ background-color: #{estilo_botao[0]}; border-radius: 5px; }}
        """)
        self.botao_fechar.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; border: none; }}
            QPushButton:hover {{ background-color: #{estilo_botao[1]}; border-radius: 5px; }}
        """)
        self.botao_home.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; border: none; }}
            QPushButton:hover {{ background-color: #{estilo_botao[0]}; border-radius: 5px; }}
        """)

    def aplicar_estilo_light(self):
        self._aplicar_estilo_base(False)
        
        # Aplicar estilos específicos dos painéis através de seus próprios métodos
        for panel in [self.automacao_coleta, self.gui_processamento_agitel, self.organizacao_pastas]:
            if hasattr(panel, 'apply_styles'):
                panel.apply_styles(False)

    def aplicar_estilo_dark(self):
        self._aplicar_estilo_base(True)
        
        # Aplicar estilos específicos dos painéis através de seus próprios métodos
        for panel in [self.automacao_coleta, self.gui_processamento_agitel, self.organizacao_pastas]:
            if hasattr(panel, 'apply_styles'):
                panel.apply_styles(True)