import os
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon
from GerenEstilos import (
    estilo_sheet_light, estilo_label_light, estilo_combo_box_light,
    campo_qline_light, estilo_log_light, estilo_sheet_dark, estilo_label_dark, estilo_combo_box_dark,
    campo_qline_dark, estilo_log_dark
)

class GerenTema:
    def __init__(
        self, 
        main_window, 
        central_widget, 
        barra_titulo, 
        funcionalidades_combo,
        automacao_coleta, 
        gui_processamento_agitel,
        botao_modo, 
        botao_minimizar, 
        botao_fechar,
        botao_home
    ):
        self.main_window = main_window
        self.central_widget = central_widget
        self.barra_titulo = barra_titulo
        self.funcionalidades_combo = funcionalidades_combo
        self.automacao_coleta = automacao_coleta
        self.gui_processamento_agitel = gui_processamento_agitel
        self.botao_modo = botao_modo
        self.botao_minimizar = botao_minimizar
        self.botao_fechar = botao_fechar
        self.botao_home = botao_home  # Novo atributo
        self.settings_path = main_window.settings_path
        self.widgets = []
        self._modo_escuro = False
        self.load_settings()
        self.update_icons()
        self.register_widget(central_widget)
        self.register_widget(barra_titulo)
        self.register_widget(funcionalidades_combo)
        self.register_widget(automacao_coleta)
        self.register_widget(gui_processamento_agitel)
        self.register_widget(botao_modo)
        self.register_widget(botao_minimizar)
        self.register_widget(botao_fechar)
        self.register_widget(botao_home)  # Registrar o novo botão
        self.aplicar_tema_inicial()

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
        self.widgets.append(widget)
        if hasattr(widget, 'apply_styles'):
            widget.apply_styles(self.modo_escuro)

    def update_icons(self):
        base_path = os.path.join(os.path.dirname(__file__), "resources")
        theme_suffix = "dark" if self.modo_escuro else "light"
        
        self.botao_home.setIcon(QIcon(os.path.join(base_path, f"home_{theme_suffix}.png")))
        self.botao_modo.setIcon(QIcon(os.path.join(base_path, f"ui_{theme_suffix}.png")))
        self.botao_minimizar.setIcon(QIcon(os.path.join(base_path, f"ui_minimize_{theme_suffix}.png")))
        self.botao_fechar.setIcon(QIcon(os.path.join(base_path, f"ui_exit_{theme_suffix}.png")))
        
        if hasattr(self.automacao_coleta, 'update_icons'):
            self.automacao_coleta.update_icons(theme_suffix)
        
        if hasattr(self.gui_processamento_agitel, 'update_icons'):
            self.gui_processamento_agitel.update_icons(theme_suffix)

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


    def aplicar_estilo_light(self):
        self.central_widget.setStyleSheet(estilo_sheet_light())
        self.barra_titulo.setStyleSheet(estilo_sheet_light())
        self.funcionalidades_combo.setStyleSheet(estilo_combo_box_light())
        self.automacao_coleta.setStyleSheet(estilo_sheet_light())
        self.automacao_coleta.campo_pasta.setStyleSheet(campo_qline_light())
        self.automacao_coleta.campo_planilha.setStyleSheet(campo_qline_light())
        self.automacao_coleta.combo_operadora.setStyleSheet(estilo_combo_box_light())
        self.automacao_coleta.log_tecnico.setStyleSheet(estilo_log_light())
        self.automacao_coleta.log_faturas.setStyleSheet(estilo_log_light())
        self.automacao_coleta.rotulo_pasta.setStyleSheet(estilo_label_light())
        self.automacao_coleta.rotulo_planilha.setStyleSheet(estilo_label_light())
        self.automacao_coleta.rotulo_operadora.setStyleSheet(estilo_label_light())
        self.botao_modo.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #e0e0e0; border-radius: 5px; }")
        self.botao_minimizar.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #e0e0e0; border-radius: 5px; }")
        self.botao_fechar.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #ff6b6b; border-radius: 5px; }")
        self.botao_home.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                border: none; 
            } 
            QPushButton:hover { 
                background-color: #e0e0e0; 
                border-radius: 5px; 
            }
        """)

    def aplicar_estilo_dark(self):
        self.central_widget.setStyleSheet(estilo_sheet_dark())
        self.barra_titulo.setStyleSheet(estilo_sheet_dark())
        self.funcionalidades_combo.setStyleSheet(estilo_combo_box_dark())
        self.automacao_coleta.setStyleSheet(estilo_sheet_dark())
        self.automacao_coleta.campo_pasta.setStyleSheet(campo_qline_dark())
        self.automacao_coleta.campo_planilha.setStyleSheet(campo_qline_dark())
        self.automacao_coleta.combo_operadora.setStyleSheet(estilo_combo_box_dark())
        self.automacao_coleta.log_tecnico.setStyleSheet(estilo_log_dark())
        self.automacao_coleta.log_faturas.setStyleSheet(estilo_log_dark())
        self.automacao_coleta.rotulo_pasta.setStyleSheet(estilo_label_dark())
        self.automacao_coleta.rotulo_planilha.setStyleSheet(estilo_label_dark())
        self.automacao_coleta.rotulo_operadora.setStyleSheet(estilo_label_dark())
        self.botao_modo.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #444444; border-radius: 5px; }")
        self.botao_minimizar.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #444444; border-radius: 5px; }")
        self.botao_fechar.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #ff6b6b; border-radius: 5px; }")
        self.botao_home.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                border: none; 
            } 
            QPushButton:hover { 
                background-color: #444444; 
                border-radius: 5px; 
            }
        """)