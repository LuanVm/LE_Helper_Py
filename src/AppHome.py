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
        caminho_logo = os.path.join(os.path.dirname(__file__), "resources", "logo.png")
        pixmap = QPixmap(caminho_logo)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(240, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            self.logo_label.setFixedSize(scaled_pixmap.size())
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_opacity_effect = QGraphicsOpacityEffect(self.logo_label)
        self.logo_label.setGraphicsEffect(self.logo_opacity_effect)
        self.logo_opacity_effect.setOpacity(0)

    def setup_squares(self):
        def get_base_orange():
            # Gera valores base para tons de laranja
            red = random.randint(200, 255)
            green = random.randint(100, 200)
            blue = random.randint(0, 50)
            return (red, green, blue)

        def lighten_orange(rgb, amount=40):
            # Clareia a cor mantendo o tom alaranjado
            return (
                min(rgb[0] + amount, 255),
                min(rgb[1] + amount, 255),
                max(rgb[2] - amount//2, 0)
            )

        def create_gradient(base_rgb):
            # Cria variações para o gradiente
            variation = random.randint(20, 60)
            start_r = min(base_rgb[0] + variation, 255)
            start_g = min(base_rgb[1] + variation//2, 255)
            start_b = max(base_rgb[2] - variation//3, 0)
            
            return (
                f"#{base_rgb[0]:02x}{base_rgb[1]:02x}{base_rgb[2]:02x}",
                f"#{start_r:02x}{start_g:02x}{start_b:02x}"
            )

        setores = [
            "Automação", "Planilhamento", "Financeiro",
            "Setor 4", "Setor 5", "Setor 6"
        ]
        
        self.squares = []
        self.button_effects = []  # Nova lista para armazenar os efeitos de opacidade
        
        for i, setor in enumerate(setores):
            btn = QPushButton(setor, self)
            btn.setFixedSize(150, 150)
            btn.setObjectName("sector_button")

            # Configura efeito de opacidade igual à logo
            btn_opacity = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(btn_opacity)
            btn_opacity.setOpacity(0)  # Inicia invisível
            self.button_effects.append(btn_opacity)

            # Gera cores base
            base_orange = get_base_orange()
            start_color, end_color = create_gradient(base_orange)
            
            # Cores para hover
            hover_rgb = lighten_orange(base_orange, 60)
            hover_start = f"#{hover_rgb[0]:02x}{hover_rgb[1]:02x}{hover_rgb[2]:02x}"
            hover_end = f"#{min(hover_rgb[0]+30,255):02x}{min(hover_rgb[1]+30,255):02x}{max(hover_rgb[2]-20,0):02x}"

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
                    border: 1px solid rgba(255, 255, 255, 0.6);
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
