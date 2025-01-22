import colorsys
import os
import random
from functools import partial
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtSignal, QParallelAnimationGroup, QEasingCurve
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, 
                            QGridLayout, QPushButton, QGraphicsOpacityEffect)

class HomeScreen(QWidget):
    square_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setup_logo()
        self.setup_squares()
        self.setup_layout()
        self.setup_animations()

    def setup_logo(self):
        self.logo_label = QLabel(self)
        caminho_logo = os.path.join(os.path.dirname(__file__), "resources", "logo_completa.png")
        pixmap = QPixmap(caminho_logo)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(480, 240, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            self.logo_label.setFixedSize(scaled_pixmap.size())
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_opacity_effect = QGraphicsOpacityEffect(self.logo_label)
        self.logo_label.setGraphicsEffect(self.logo_opacity_effect)
        self.logo_opacity_effect.setOpacity(0)

    def setup_squares(self):
        def get_base_orange():
            # Gera tons quentes com predominância de laranja
            return (
                random.randint(200, 255),  # Red
                random.randint(50, 150),   # Green
                random.randint(0, 50)      # Blue
            )

        def adjust_hsl(rgb, h_delta=0, s_delta=0, l_delta=0):
            # Converte RGB para HSL
            r, g, b = [x/255.0 for x in rgb]
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            
            # Ajusta os valores
            h = (h + h_delta) % 1.0
            s = max(min(s + s_delta, 1.0), 0.4)
            l = max(min(l + l_delta, 1.0), 0.3)
            
            # Converte de volta para RGB
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return (
                int(r * 255),
                int(g * 255),
                int(b * 255)
            )

        def create_gradient(base_rgb):
            # Cria gradiente análogo com variação controlada
            color1 = adjust_hsl(base_rgb, h_delta=0.02, s_delta=-0.1, l_delta=0.05)
            color2 = adjust_hsl(base_rgb, h_delta=-0.02, s_delta=0.1, l_delta=-0.05)
            return (
                f"#{color1[0]:02x}{color1[1]:02x}{color1[2]:02x}",
                f"#{color2[0]:02x}{color2[1]:02x}{color2[2]:02x}"
            )

        def create_hover_gradient(base_rgb):
            # Gradiente complementar suave
            base_h = colorsys.rgb_to_hls(*[x/255.0 for x in base_rgb])[0]
            complement_h = (base_h + 0.1) % 1.0  # Deslocamento de 36 graus
            
            # Converte para RGB
            r1, g1, b1 = colorsys.hls_to_rgb(complement_h, 0.7, 0.6)
            r2, g2, b2 = colorsys.hls_to_rgb(base_h, 0.8, 0.4)
            
            return (
                f"#{int(r1*255):02x}{int(g1*255):02x}{int(b1*255):02x}",
                f"#{int(r2*255):02x}{int(g2*255):02x}{int(b2*255):02x}"
            )

        setores = [
            "Coleta de faturas", "Planilhamento", "Financeiro",
            "Indisponível", "Indisponível", "Indisponível"
        ]
        
        self.squares = []
        self.button_effects = []
        
        for i, setor in enumerate(setores):
            btn = QPushButton(setor, self)
            btn.setFixedSize(150, 150)
            btn.setObjectName("sector_button")

            # Efeito de opacidade
            btn_opacity = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(btn_opacity)
            btn_opacity.setOpacity(0)
            self.button_effects.append(btn_opacity)

            # Geração de cores
            base_orange = get_base_orange()
            start_color, end_color = create_gradient(base_orange)
            hover_start, hover_end = create_hover_gradient(base_orange)

            style = f"""
                QPushButton {{
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 {start_color}, stop:1 {end_color});
                    border: 0;
                    border-radius: 12px;
                    color: #FFFFFF;
                    font-family: 'Segoe UI Black', Roboto, Helvetica, Arial, sans-serif;
                    font-size: 12px;
                    font-weight: 500;
                    padding: 8px 24px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background: qlineargradient(spread:pad, x1:0.5, y1:0.5, x2:1, y2:1,
                        stop:0 {hover_start}, stop:1 {hover_end});
                    border: 1px solid rgba(255, 255, 255, 0.8);
                }}
                QPushButton:focus {{
                    outline: none;
                }}
            """
            btn.setStyleSheet(style)
            btn.clicked.connect(partial(self.square_clicked.emit, i))
            self.squares.append(btn)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        for i in range(6):
            self.grid_layout.addWidget(self.squares[i], i//3, i%3)

        self.squares_container = QWidget()
        self.squares_container.setLayout(self.grid_layout)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)

    def setup_layout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.squares_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def setup_animations(self):
        self.logo_anim = QPropertyAnimation(self.logo_opacity_effect, b"opacity")
        self.logo_anim.setDuration(1500)
        self.logo_anim.setStartValue(0)
        self.logo_anim.setEndValue(1)

        # Novas animações para os botões
        self.button_anims = []
        for effect in self.button_effects:
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(1500)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutQuad)  # Suaviza a curva de animação
            self.button_anims.append(anim)
        
        # Grupo de animações para sincronizar
        self.parallel_anim = QParallelAnimationGroup()
        self.parallel_anim.addAnimation(self.logo_anim)
        for anim in self.button_anims:
            self.parallel_anim.addAnimation(anim)
        
        self.parallel_anim.start()
